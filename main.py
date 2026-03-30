# -*- coding: utf-8 -*-
import argparse
from generator import ForecastInput, generate_forecast, generate_bundle, to_json


def parse_args():
    p = argparse.ArgumentParser(description="Telegram prediction bot text generator")
    p.add_argument("--age-group", required=True, choices=["до 18", "18–25", "25+"])
    p.add_argument("--relationship", required=True, choices=["single", "taken"])
    p.add_argument("--focus", required=True, choices=["money", "love", "career"])
    p.add_argument("--photo", action="store_true")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument(
        "--mode",
        default="bundle",
        choices=["single", "bundle", "telegram"],
        help="single = old flat json, bundle = free/paid/telegram, telegram = only telegram payloads"
    )
    return p.parse_args()


def main():
    args = parse_args()
    data = ForecastInput(
        age_group=args.age_group,
        relationship=args.relationship,
        focus=args.focus,
        photo=args.photo,
        seed=args.seed
    )
    if args.mode == "single":
        payload = generate_forecast(data)
    else:
        bundle = generate_bundle(data)
        if args.mode == "telegram":
            payload = bundle["telegram"]
        else:
            payload = bundle
    print(to_json(payload))


if __name__ == "__main__":
    main()
