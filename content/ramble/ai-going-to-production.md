---
title: SRE Agent goes to production*
date: 2026-10-11
excerpt: Production isn't a playground — how much access do we give an AI agent?
description: SRE Agent goes to production* — on access, sandboxes, and why prod isn't a playground.
post_vibe: "*sike"
page_class: page--post
---

When investigating an incident, we usually gather and correlated information from sources like logs, metrics, traces, deployment history, Kubernetes events, and perhaps database state to get a whole picture of what is going on.

A spike in http 500s might be an unannounced deployment, a growing queue might be cause by crashing consumers. One barely concluds the cause by just reading the error message and codebase.

Before an agent can perform magic, I reckon it'd need the access to those sources as well.

But production is not a playground. Giving an agent unrestricted access to everything isn't a reasonable solution. A database query could expose sensitive information or overload a production database; a Kubernetes command could restart a critical workload; a Terraform change could replace a resource that another service depends on.

So we have a dilemma: the less access we give an agent, the less it can see; the more access we give it, the more damage it could potentially do.

I did some shallow research into existing approaches — writing it down here mostly for my own learning.

## Ways around this

### Give the agent a restricted view of production

Instead of giving an agent unrestricted access to production, we can expose a carefully selected set of tools and data. So it has (hopefully) enough context to investigate incidents but can't automatically applying every possible fix.

For example:

- **Logs and metrics:** Let the agent query centralized logs, traces, dashboards, deployment history, and Kubernetes events through read-only access. This gives it evidence to investigate many incidents without allowing it to change production systems. Access should still be scoped carefully, since logs and traces can contain sensitive information.
- **Database:** Use read replicas, read-only roles, masked views, or a query gateway that enforces query limits and timeouts. For more sensitive data, require additional approval before allowing access to unmasked records or bulk exports. An anonymized production snapshot in staging is another option. Each approach involves trade-offs: read replicas can lag behind production, masking can hide useful debugging details, and snapshots can become stale.
- **Kubernetes:** Start with a read-only service account scoped by RBAC to the namespaces and resources the agent needs. It can inspect pod health, logs, events, and deployment status without being allowed to restart workloads or modify resources. Be careful about what it can read, too: logs, environment variables, and other diagnostic information may contain secrets or sensitive data.
- **Terraform:** Let the agent inspect infrastructure configuration and generate a Terraform plan, but keep applying infrastructure changes behind a human-reviewed pull request and a controlled CI pipeline. A plan helps reviewers understand the proposed changes, but it doesn't guarantee that the changes are safe. Access to Terraform state and cloud credentials should also be restricted, and the apply step must remain protected.
- **A semantic layer over production data:** Rather than letting the agent query arbitrary database tables, we can expose meaningful concepts such as order failure rates, queue lag, inventory discrepancies, or service latency through a curated dataset or predefined queries. This gives the agent a simpler, more controlled interface to the information it needs. Pre-aggregated data can also make queries cheaper and faster. Of course, there are trade-offs: a curated dataset might omit the one obscure field that explains an incident, while aggregated metrics might hide a failure affecting only one customer or request. Building and maintaining this layer takes engineering effort, too.

Across these approaches, we should use short-lived, least-privilege credentials and log what the agent accesses and does. If a human approves an action, the system should validate the exact operation and its parameters again at execution time, so the agent cannot modify the request after approval.

### Sandboxing: don't experiment in production

Another approach is to let the agent experiment somewhere other than production. Give it an isolated sandbox or staging environment where it can run commands, test hypotheses, execute scripts, and try proposed fixes without directly affecting real customer traffic.

For example, suppose an agent suspects that a recent configuration change is causing a service to crash. It could inspect the relevant configuration, reproduce the problem in staging, and test a correction before recommending it. For code and infrastructure changes, it could generate a patch, run tests, and produce a Terraform plan for review instead of immediately modifying production.

But staging is not production. It may have different traffic patterns, data volumes, permissions, dependencies, or failure modes. A fix that works perfectly there might behave very differently under production load. A sandbox also needs genuine isolation: if it shares critical resources with production or has credentials that allow production changes, it may not be as safe as it appears.

Most importantly, isolating the agent's execution environment doesn't automatically isolate its actions in external systems. If an agent running in a sandbox can call a production API using credentials with write access, it can still make production changes.

So sandboxing works best alongside restricted permissions. Let the agent experiment in a controlled environment, and give it only the minimum production access needed to investigate the real incident.

In practice, people usually combine the approaches: use read-only production access to gather real evidence, use staging or a sandbox to test possible solutions, and require approval before changes that could have a significant impact on production.

## What to keep in mind when giving AI access to production

Even with restricted access and sandboxing, we still need to decide how much autonomy an AI agent should have.

For now, **reversibility is a useful starting point.** Reading logs, summarizing incidents, and proposing fixes are relatively low-risk. Deleting production data or running irreversible migrations is another story. Even a reversible action, like restarting a service, can cause downtime before it's undone, repeatedly restarting a failing service can turn a small problem into a prolonged outage.

So rather than drawing the line between read and write access, we should consider an action's impact, scope, and recoverability. An agent might restart a non-critical staging service automatically, while production changes require human approval.

**Pick the right things to delegate.** Not every problem needs AI. For predictable failures, alerts and well-tested runbooks may be enough. KEDA, for example, can scale workloads based on queue metrics, but adding consumers won't necessarily fix a dead-letter queue full of messages that consistently fail processing. AI becomes more useful when the cause needs further investigation.

## Sooo, are we there yet?

There's still work to do before we can trust AI to operate autonomously in production. We need enough context to make it useful, enough restrictions to contain its mistakes, and clear boundaries around what it can do without human approval.

Maybe the question isn't whether AI is ready for production, but whether we've built production systems that are ready for AI.
