from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Task, ShopItem


class Command(BaseCommand):
    help = "Seed tasks, shop items and demo user."

    def handle(self, *args, **options):
        # ── Tasks ──
        for slug, title, order in [
            ("task-10-ribbon", "Ribbon and Bows", 10),
            ("task-12-cookie", "Cookie Share",    12),
            ("task-14-pizza",  "Pizza Division",  14),
        ]:
            Task.objects.get_or_create(
                slug=slug,
                defaults={"title": title, "order": order, "is_available": True}
            )
        self.stdout.write(self.style.SUCCESS("✅ Tasks seeded."))

        # ── Shop Items ──
        shop_items = [
            # ── RIBBON COLOUR PACKS ──
            dict(name="Red Ribbon",
                 task_tag="ribbon", theme_key="colour_red", emoji="🔴", cost=2,
                 description="Turn the ribbon bold crimson red. Classic and striking!"),
            dict(name="Blue Ribbon",
                 task_tag="ribbon", theme_key="colour_blue", emoji="🔵", cost=2,
                 description="Change the ribbon to a cool ocean blue."),
            dict(name="Rainbow Ribbon",
                 task_tag="ribbon", theme_key="colour_rainbow", emoji="🌈", cost=4,
                 description="A gorgeous fading rainbow ribbon — red, orange, yellow, green, blue, purple!"),
            dict(name="Glitter Gold",
                 task_tag="ribbon", theme_key="colour_glitter", emoji="✨", cost=5,
                 description="Sparkling golden glitter ribbon. Fancy!"),

            # ── COOKIE CHARACTER PACKS ──
            dict(name="Jungle Pack",
                 task_tag="cookie", theme_key="jungle", emoji="🌴", cost=5,
                 description=(
                     "Replaces all characters with jungle animals!\n"
                     "Mouse → 🐯 Tiger\n"
                     "Wolf → 🐒 Monkey\n"
                     "Human → 🦜 Parrot\n"
                     "Lion → 🐘 Elephant"
                 )),
            dict(name="Ocean Pack",
                 task_tag="cookie", theme_key="ocean", emoji="🌊", cost=5,
                 description=(
                     "Dive underwater with sea creatures!\n"
                     "Mouse → 🦀 Crab\n"
                     "Wolf → 🐬 Dolphin\n"
                     "Human → 🦈 Shark\n"
                     "Lion → 🐋 Whale"
                 )),
            dict(name="Space Pack",
                 task_tag="cookie", theme_key="space", emoji="🚀", cost=7,
                 description=(
                     "Aliens sharing space-cookies in the galaxy!\n"
                     "Mouse → 👾 Alien Jr\n"
                     "Wolf → 🛸 UFO\n"
                     "Human → 🤖 Robot\n"
                     "Lion → 🌍 Planet"
                 )),

            # ── PIZZA THEME PACKS ──
            dict(name="Halloween Pack",
                 task_tag="pizza", theme_key="halloween", emoji="🎃", cost=5,
                 description=(
                     "Spooky Halloween theme! Characters wear costumes:\n"
                     "🎃 Ghost, 🧟 Zombie, 🧛 Vampire, 🧙 Witch\n"
                     "Orange & black pizza!"
                 )),
            dict(name="Christmas Pack",
                 task_tag="pizza", theme_key="christmas", emoji="🎄", cost=5,
                 description=(
                     "Festive Christmas theme! Characters become:\n"
                     "🎅 Santa, 🤶 Mrs Claus, 🦌 Reindeer, ⛄ Snowman\n"
                     "Red & green Christmas pizza!"
                 )),
        ]

        for item_data in shop_items:
            ShopItem.objects.get_or_create(
                name=item_data["name"],
                defaults={**item_data, "is_available": True}
            )
        self.stdout.write(self.style.SUCCESS(f"✅ {len(shop_items)} shop items seeded."))

        # ── Demo User ──
        User = get_user_model()
        if not User.objects.filter(username="demochild").exists():
            User.objects.create_user(username="demochild", password="demo12345")
            self.stdout.write(self.style.SUCCESS("✅ Demo user: demochild / demo12345"))
        else:
            self.stdout.write("ℹ️  Demo user already exists.")
