> DRAFT: items in [square brackets] are placeholders. Replace them with real results after you build and test. Delete anything that did not actually happen. The rules require the project to work as described.

## Inspiration

In villages along forest edges in Chhattisgarh and Uttarakhand, the first warning of a wild animal is often the encounter itself.

Chhattisgarh has only about 1% of India's elephants, yet it recorded 303 elephant-related human deaths between 2019 and 2024, roughly 15% of the national total. In Uttarakhand, more than 500 people have died in elephant attacks over the past decade, with Dehradun among the worst-affected districts. Around Dehradun and Mussoorie, leopards moving through hill settlements at dusk are behind nearly half of the state's wildlife-attack deaths, with over 400 people killed since 2000 (as of a 2022 report).

**Two recent cases that shaped the design**

*Jashpur, Chhattisgarh (August 2026).* A herd of about 16 elephants had been camping in the forest near Ghughri village for several days. Late one night the herd came out of the forest, and a 70-year-old man sleeping in his mud hut at the forest edge was killed. In the weeks before, attacks in neighbouring Korba and Raigarh districts killed at least six people between late June and early August, including a farmer walking to his field and a man who stepped outside his house before dawn.

*Thano range, Dehradun (November 2025).* A 12-year-old boy walking to a temple with his parents on the outskirts of Dehradun was killed by an elephant one evening. Residents said a female elephant with her calf had been moving through the area for the past few days, and officials afterwards told people to avoid the forest route.

In both reports, the animal was known to have been in the area for days. WildWatch is aimed at the gap between "there is an elephant somewhere nearby" and "one is moving toward this path right now", the specific, timely warning that reaches the people about to be on that path, at night or at dusk.

Warning systems also tend to fail in two ways. They arrive too late, or they fire so many false alarms that people stop listening. We wanted an early-warning system where an alert is rare enough to trust and early enough to act on.

Sources: [ETV Bharat, Jashpur (Aug 2026)](https://www.etvbharat.com/en/state/elephant-attack-in-jashpur-elderly-man-dies-human-elephant-conflict-in-cg-enn26081008015), [Daily Pioneer, Korba (Aug 2026)](https://dailypioneer.com/news/wild-elephant-tramples-man-to-death-in-chhattisgarhs-korba), [ETV Bharat, Dehradun (Nov 2025)](https://www.etvbharat.com/en/state/12-year-old-boy-trampled-to-death-by-elephant-in-dehradun-enn25112800192)

[Add one or two sentences about your personal connection to these regions or a conversation with someone affected. Judges score "genuine understanding of the problem space".]

## What it does

WildWatch is a network of camera nodes that closes the whole loop, not just detection:

- **Detect:** a Raspberry Pi 4 running a small vision model spots animal-like movement on the device, even with no internet.
- **Verify:** the cropped frame goes to an NVIDIA vision model on Nebius Token Factory, which decides whether it is really an elephant, leopard, or other animal, or just a person, cattle, or a shadow. This filters false alarms.
- **Predict:** an AI agent combines verified sightings with node positions and recent history to estimate where the animal is heading and roughly when it could get there.
- **Act:** it sends a plain-language alert in Hindi and English to authorized contacts on Telegram, and triggers a light and sound deterrent at the node ahead of the animal's path.
- **Learn:** recipients tap *Confirmed*, *False alarm*, or *Animal left*. A node that keeps false-triggering becomes less sensitive.

Safety is built in. The AI only proposes actions, and a guardrail layer in plain code enforces the rules: deterrents are non-harmful (light and sound only), they fire only after verification, they never push an animal toward a settlement, and alerts go only to allowlisted recipients. If the internet drops, the node keeps detecting, flashes its strobe, and syncs its queued events later.

## How we built it

**On the node (Raspberry Pi 4, 4 GB):**
- Camera capture (Pi camera / USB webcam), YOLO-nano exported to NCNN for fast CPU inference, multi-frame tracking, and a direction/approach estimate from bounding-box movement
- A trigger layer with per-node confidence thresholds and cooldowns
- A SQLite offline queue, a local fallback rule, and a command listener
- GPIO control of a strobe and buzzer through a relay/MOSFET stage

**In the cloud (Nebius):**
- A FastAPI backend deployed on [Nebius Serverless Endpoint / DevPod], with an event database
- **Nebius Token Factory** for runtime inference: [vision model ID] for frame verification and [NVIDIA Nemotron model ID] for the tool-calling agent
- Agent tools: recent events, topology, node status, next-node prediction, deterrent trigger, Telegram alert, human confirmation, and [Tavily web context, if built]
- A guardrail module, a Telegram bot with feedback buttons, and a dashboard showing the event timeline and an "Explain my alert" panel

**Evaluation:** a labelled test set of [N] clips and frames, including hard negatives like people, cattle, dogs, branches, and shadows. We compared edge-only detection against edge plus cloud verification and logged detection-to-alert latency. [Describe whether you ran batch evaluation on Nebius Serverless Jobs.]

All code is open source under [MIT / Apache-2.0].

## Challenges we ran into

[Edit this list to match what actually happened.]

- **Running detection at a usable frame rate on a Pi 4.** We had to [reduce input size / export to NCNN / skip frames / add cooling]. Result: [X FPS].
- **Common detectors don't know every local animal.** COCO-trained models have no leopard, boar, deer, or monkey class, so we used the edge model only as a trigger and let the cloud model name the species.
- **Reliable structured output.** Getting consistent JSON verdicts and tool calls from the models needed [prompt changes / schema validation / retries].
- **Balancing false alarms against misses.** [Describe the threshold tuning and what trade-off you chose.]
- **Night operation.** A standard camera struggles in the dark, which is when many encounters happen. [Describe what you tried, e.g. NoIR camera + IR illuminator, or state it as a limitation.]
- **Designing safe automation.** A deterrent that pushes an animal toward people is worse than none, which led to the guardrail layer.
- **Test data.** We used [own footage / public-domain clips] because we needed content we had rights to.

## Accomplishments that we're proud of

[Only include results you actually measured.]

- A complete physical loop working live: detect, verify, predict, alert, and deterrent, on real hardware
- Cloud verification cut false alarms from [X%] to [Y%] on our test set
- Median detection-to-alert latency of [N seconds]
- The node kept responding with the network cut: first strobe in [N seconds], full sync after reconnect
- A feedback loop that visibly changes behavior: [describe the before/after on one node]
- Guardrails that blocked [N] unsafe actions during testing

## What we learned

[Edit to reflect your real experience.]

- The edge and cloud split matters. A cheap, trigger-happy model on the device plus a smarter verifier in the cloud beats either alone.
- The model works best when it picks actions with tools, and plain-code guardrails own the hard safety limits.
- Trust is the product. In an alert system, fewer, better alerts matter more than catching everything.
- [What you learned about Token Factory, NVIDIA models, or running edge AI on a Pi.]

## What's next for WildWatch

- **Field pilots:** test with communities and forest authorities in forest-edge areas like those in Chhattisgarh and around Dehradun and Mussoorie, and learn what alert channels people actually use.
- **More local species:** fine-tune the edge detector for leopard, wild boar, deer, and monkey, using synthetic data generated on Nebius Serverless Jobs.
- **Night and weather:** infrared and thermal cameras, plus solar-powered nodes with LTE backup.
- **Reaching everyone:** voice calls, sirens, and community radio for people without smartphones, and alerts in more local languages.
- **Network intelligence:** learn animal movement corridors from accumulated sightings to improve prediction.
- **Privacy by design:** role-based access and coarse location sharing, since wildlife location data can be sensitive.
