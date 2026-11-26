# The World — 26 November 2026

[![bounty](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Nadanese93/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Nadanese93/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page that sums up the world news of **Thursday, 26 November 2026** in one image. The program draws the whole 1024×1024 page with Python 3.13 standard library only — its own PNG encoder, its own 5×7 bitmap font, and all artwork drawn programmatically with flat shapes. No network, no external fonts or images, fully deterministic (two runs write byte-identical files).

## The stories

1. **Tanker fire kills 31 in Cairo** — A fuel tanker crashed and ignited a massive fire on a Cairo highway; at least 31 people were killed. Source: BBC, 26 November 2026.
2. **Markets plunge on AI fears** — US stocks fall sharply, the Nasdaq down almost 4% as AI fears intensify; the Trump administration proposes new Section 301 tariffs, hitting China hardest at nearly 45%. Sources: market reporting, 26 November 2026.
3. **Macy's parade postponed** — Macy's 100th Thanksgiving Day Parade in New York is postponed from Thursday to Saturday for the first time ever, as powerful winds bear down. Source: 26 November 2026.
4. **Pakistan's first astronaut reaches Tiangong** — Pakistan's Muhammad Zeeshan Ali becomes the first foreign astronaut to travel to China's Tiangong space station, on the Shenzhou-24 mission. Source: 26 November 2026.
5. **Ukraine strikes Russian air base** — Ukraine says it struck a major Russian air base, damaging five planes; Russia's own figures show it has lost nearly 500,000 people in the Ukraine war. Source: 26 November 2026.
6. **North Korea expels Swiss diplomat** — North Korea expels a Swiss diplomat in a sanctions row and orders Switzerland to close its diplomatic office in Pyongyang; Kim Jong Un calls for wider deployment of tactical nuclear weapons. Source: 26 November 2026.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024×1024 PNG, under 1 MiB). Run it twice and the files are byte-identical. With `MAKEFUN_OUTPUT_DIR` unset, the program writes to `out/`.
