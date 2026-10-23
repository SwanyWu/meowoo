---
title: Adapt and Improvise
date: 2026-10-10
excerpt: Six years ago I'd have laughed if you said AI was coming for my job.
description: On AI at work — Adapt and Improvise.
---

## It is getting real!

Six years ago, if you'd told me, “AI is coming for your job,” I'd have laughed. It wrote simple, even buggy code based on whatever I copy-pasted into it. Meanwhile, I was doing the real stuff: figuring out requirements, reviewing code, juggling context, and shipping releases. Fast-forward to today, I can type one sentence into a chat and my agent retrieves a Jira ticket, implements the requirements in advanced syntax, adds some tests with full coverage, publishes the documentation to Confluence, it'll even notify clients/users if asked. I spend a good chunk of my day talking to AI, and honestly, I still get mind-blown by how smart it can be.

The vibe has flipped too. Back then, saying “according to ChatGPT” got you weird looks. Last month, I asked a staff engineer about a relational schema, and he said, “Have you asked the AI yet?” Yep. And remember when I hated that people requested Copilot reviews on my PRs? Now it's just part of the standardized workflow (in some companies).

Oh, and I'm getting spoiled too. I once asked AI how many characters were in “ThisLooongAssString.” I could have counted. That's the moment I realised my brain was quietly outsourcing the most ridiculous little tasks.

Somewhere along the way, I went from “ugh” to “wow” and barely noticed the switch.

## But not perfect!!

AI is far from mastering every aspect of my work.

Production isn't a playground. When a database goes down, a pod keeps crash-looping, a dead-letter queue backs up, or sudden traffic spikes demand extra replicas, real stakes are involved. I doubt many engineers would be bold enough to give AI agents (temporary) permission to restart production services, alter infrastructure, or run arbitrary production database queries.

And if an entire data center loses power? AI can help coordinate the response, but a human still has to deal with the physical infrastructure. At least AI can help draft the post-mortem afterward.

AI hasn't mastered every repository setup, either. In my experience, it handles systematic refactoring (e.g. standardizing error handling, changing API contracts) noticeably better in a monorepo than polyrepo structure. (Though to be fair, I might still be refining my workflow, as I see engineers praising synthetic monorepo tooling like Nx Polygraph).

Ultimately, AI lacks legal accountability and organizational authority. End-to-end sanity checks, integration tests, and compliance audits aren't just technical exercises—they're exercises in cross-team orchestration, environment alignment, and stakeholder management. Someone still has to chase teams, negotiate trade-offs, and take ultimate responsibility for decisions.

That someone is still human.

## Suppose it's perfect?

The Industrial Revolution didn't make craftsmanship disappear. Suppose AI eventually does most of what we're paid to do. Maybe we'd build software just for fun instead. People still bake bread when buying a loaf is easier. We hand shape clay sculptures when cheap ones are available at IKEA. We spend hours practising an instrument when listening to a recording would be much more convenient. We even spend high price building our own mechanical keyboards and Nixie tube clocks. Funny dude just keeps a chives-chopping streak on reddit.

But there's a catch: we'd need to be able to afford that life. Because productivity gains don't automatically become free time. They can become higher profits, lower prices, more consumption, or more output. How those gains are distributed is a social and political choice, not something technology decides for us. I suddenly sound like a philosopher…

And maybe we'll have to rethink why a person's right to a comfortable life is so closely tied to their ability to sell their time. Until then, the practical advice is to keep up with the technology and learn the part you enjoy. (me thinks)

## What I Really Miss: The Craft and the Epiphany

Do I sound like a masochist if I say I miss being consumed by a single problem for days?

I miss having a tricky requirement live rent-free in my head, turning it over while walking or showering, debating it with a colleague, and eventually landing on a plan that neither of us could have come up with alone. I was deeply in it. I knew the rationale behind every odd edge case, every rejected alternative, and every trade-off we reluctantly accepted.

Four years ago, I built the refund flow for an e-commerce platform. We had this massive switch...case statement covering over 20 distinct refund scenarios (missing parcels, canceled orders, partial fulfillments, duplicates, and more). It was built on meticulous historical event analysis, rigorous documentation reviews, and endless interviews with account managers. I remember we'd discover some new strange cases every time we tweak the query or discover one more slack thread. One colleague even memorized the 13-digit EANs for our top 50 most frequently refunded products. Whenever an alert fired, they'd look at the product code and immediately go, "Ugh, it's that Chromecast again." (A skill as niche and entertainingly useless as reciting digits of Pi).

Today, I can type a single prompt into an AI, and the generated output is honestly better.

And yet, something feels lost.

My role has subtly shifted from creating to reacting. I've become an editor evaluating someone else's good work. I can challenge it, refine it, and decide whether it's correct, but I miss the intellectual struggle of forging the path myself.

Simply reviewing a generated answer just doesn't deliver that same spark.

Now, I'm trying to reclaim that kind of joy outside of work and honestly, who would complain too much about a bit more life :-P
