import array
import asyncio
import math
import random

import pygame

# CONTROLS
#   LEFT / RIGHT = move       SPACE = jump (or fly up as a dragon)
#   X = fire / swing          L = switch weapon
#   Z = use ability           Q = switch ability
#   UP / DOWN = fly (dragon mode only)
#   R = restart (when game over)
#
# CHEAT CODES (just type the word on the keyboard)
#   weapons:    pistol  shotgun  rifle  smg  sword  firesword  guitar  dragon  luffy
#   abilities:  fireball  shield  toxic  nuke  recruit

# try to set up sound (if the device has no sound, the game still works)
try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
except Exception:
    pass

pygame.init()

# ---------- settings (change these to tweak the game) ----------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
FPS = 60

GROUND_HEIGHT = 50
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

PLAYER_SIZE = 40
PLAYER_SPEED = 5
GRAVITY = 1
JUMP_POWER = -15
MAX_HEALTH = 100
INVINCIBLE_FRAMES = 60

ENEMY_SIZE = 40
ENEMY_DAMAGE = 20
STOMP_MARGIN = 15

ITEM_SIZE = 20
HEAL_AMOUNT = 30

CHUNK_WIDTH = 400
LOOKAHEAD = SCREEN_WIDTH
START_WORLD_END = 1400
CAMERA_OFFSET = 100

# boss settings
BOSS_EVERY = 50
BOSS_SIZE = PLAYER_SIZE * 2
BOSS_HEALTH = 25
BOSS_SPEED = 2
BOSS_DAMAGE = 30
BOSS_POINTS = 20
BOSS_SPAWN_DISTANCE = 600

# weapon settings
ONE_PIECE_SCORE = 500
GUN_Y = 27
GUN_LENGTH = 16

WEAPON_ITEM_WIDTH = 28
WEAPON_ITEM_HEIGHT = 18
WEAPON_CHANCE = 3
MESSAGE_FRAMES = 180

LASER_LENGTH = 700
LASER_THICKNESS = 14
LASER_FRAMES = 12

# dragon settings
DRAGON_FRAMES = 600
DRAGON_SPEED = 6
DRAGON_FLY_SPEED = 6
DRAGON_COOLDOWN = 300
DRAGON_MOUTH = 30
DRAGON_FIRE_WIDTH = 26
DRAGON_FIRE_HEIGHT = 14
DRAGON_FIRE_SPEED = 9
DRAGON_FIRE_LIFE = 30
DRAGON_FIRE_DAMAGE = 1
DRAGON_FIRE_COOLDOWN = 8

# ability settings
FIREBALL_SIZE = 24
FIREBALL_SPEED = 8
FIREBALL_LIFE = 80
FIREBALL_DAMAGE = 4

SHIELD_FRAMES = 300

TOXIC_WIDTH = 220
TOXIC_HEIGHT = 110
TOXIC_FRAMES = 480
TOXIC_TICK = 20

NUKE_FRAMES = 40

MAX_ALLIES = 3
ALLY_SPEED = 4
ALLY_DAMAGE = 2
ALLY_BOSS_DAMAGE = 1
ALLY_HIT_FRAMES = 15

# guitar sound length in seconds
GUITAR_SECONDS = 0.5

# enemies stand on the ground, items float a little above it
ENEMY_Y = GROUND_Y - ENEMY_SIZE
BOSS_Y = GROUND_Y - BOSS_SIZE
ITEM_Y = GROUND_Y - 40
WEAPON_ITEM_Y = GROUND_Y - 34

# colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COIN_YELLOW = (255, 215, 0)
ENEMY_RED = (200, 30, 30)
ENEMY_PURPLE = (128, 0, 128)
BOSS_COLOR = (255, 120, 0)
HEALTH_RED = (200, 0, 0)
HEALTH_BG = (80, 80, 80)
HEALTH_GREEN = (0, 200, 0)
BULLET_COLOR = (255, 255, 0)
YELLOW = (255, 255, 0)
FIRE_ORANGE = (255, 120, 0)
LASER_RED = (255, 0, 0)
LASER_CORE = (255, 200, 200)
GUN_GRAY = (70, 70, 70)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
STEEL = (60, 80, 130)
SILVER = (200, 200, 210)
PURPLE = (150, 0, 200)
DRAGON_GREEN = (30, 160, 60)
DRAGON_DARK = (10, 90, 40)
DRAGON_BELLY = (200, 220, 100)
FIREBALL_RED = (220, 40, 0)
SHIELD_CYAN = (0, 220, 255)
SHIELD_LIGHT = (180, 245, 255)
TOXIC_GREEN = (60, 200, 60)
TOXIC_LIGHT = (170, 255, 120)
NUKE_RED = (200, 0, 60)
ALLY_BLUE = (30, 120, 255)

# ---------- pygame setup ----------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Sidescroller")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
tiny_font = pygame.font.Font(None, 22)
big_font = pygame.font.Font(None, 72)
plus_text = pygame.font.Font(None, 30).render("+", True, WHITE)

# ---------- weapon list ----------
# every weapon is a dictionary stored in WEAPONS
#   kind "gun"    = shoots bullets
#   kind "skull"  = shoots skulls
#   kind "melee"  = swings (speed = how far it reaches)
#   kind "laser"  = the One Piece cannon
#   kind "dragon" = turns you into a dragon
WEAPONS = {}


def add_weapon(key, label, color, kind, cooldown, damage, speed=0, life=0, size=0, pellets=1, length=16):
    weapon = {}
    weapon["key"] = key
    weapon["label"] = label
    weapon["color"] = color
    weapon["kind"] = kind
    weapon["cooldown"] = cooldown
    weapon["damage"] = damage
    weapon["speed"] = speed
    weapon["life"] = life
    weapon["size"] = size
    weapon["pellets"] = pellets
    weapon["length"] = length
    WEAPONS[key] = weapon


add_weapon("pistol", "PISTOL", GUN_GRAY, "gun", 15, 1, speed=10, life=60, size=12, length=12)
add_weapon("shotgun", "SHOTGUN", BROWN, "gun", 40, 1, speed=9, life=25, size=8, pellets=5, length=24)
add_weapon("rifle", "RIFLE", DARK_GREEN, "gun", 25, 3, speed=16, life=60, size=16, length=28)
add_weapon("smg", "SMG", STEEL, "gun", 6, 1, speed=12, life=45, size=10, length=18)
add_weapon("sword", "SWORD", SILVER, "melee", 20, 3, speed=55, life=8)
add_weapon("firesword", "FIRE SWORD", FIRE_ORANGE, "melee", 20, 6, speed=70, life=8)
add_weapon("guitar", "GUITAR", PURPLE, "skull", 25, 3, speed=7, life=70, size=20, length=26)
add_weapon("dragon", "DRAGON", DRAGON_GREEN, "dragon", 0, 1, length=14)
add_weapon("onepiece", "ONE PIECE", LASER_RED, "laser", 30, 0, length=GUN_LENGTH)

# weapons that can spawn on the ground (rare ones are in the list less often)
WEAPON_SPAWN_LIST = ["pistol", "pistol", "shotgun", "shotgun", "rifle", "smg"]
WEAPON_SPAWN_LIST = WEAPON_SPAWN_LIST + ["sword", "sword", "firesword", "guitar", "dragon"]

# small text labels shown above weapons lying on the ground
labels = {}
for weapon_key in WEAPONS:
    labels[weapon_key] = tiny_font.render(WEAPONS[weapon_key]["label"], True, BLACK)

ally_label = tiny_font.render("ALLY", True, BLACK)

# ---------- ability list ----------
# abilities are earned by defeating bosses.  Z = use, Q = switch
ABILITIES = {}


def add_ability(key, label, color, cooldown):
    ability = {}
    ability["key"] = key
    ability["label"] = label
    ability["color"] = color
    ability["cooldown"] = cooldown
    ABILITIES[key] = ability


# cooldown is in frames (60 frames = 1 second)
add_ability("fireball", "FIREBALL", FIRE_ORANGE, 45)
add_ability("shield", "SHIELD", SHIELD_CYAN, 900)
add_ability("toxic", "TOXIC GAS", TOXIC_GREEN, 600)
add_ability("nuke", "NUKE", NUKE_RED, 1800)
add_ability("recruit", "RECRUIT", ALLY_BLUE, 60)

# which boss gives which ability (the boss that appears at that score level)
ABILITY_REWARDS = {}
ABILITY_REWARDS[50] = "fireball"
ABILITY_REWARDS[100] = "shield"
ABILITY_REWARDS[150] = "toxic"
ABILITY_REWARDS[500] = "nuke"
ABILITY_REWARDS[600] = "recruit"

# ---------- cheat codes ----------
# type the word on the keyboard and you get the weapon
CHEATS = {}
CHEATS["pistol"] = "pistol"
CHEATS["shotgun"] = "shotgun"
CHEATS["rifle"] = "rifle"
CHEATS["smg"] = "smg"
CHEATS["submachinegun"] = "smg"
CHEATS["sword"] = "sword"
CHEATS["firesword"] = "firesword"
CHEATS["guitar"] = "guitar"
CHEATS["dragon"] = "dragon"
CHEATS["luffy"] = "onepiece"
CHEATS["onepiece"] = "onepiece"
CHEATS["fireball"] = "fireball"
CHEATS["shield"] = "shield"
CHEATS["toxic"] = "toxic"
CHEATS["toxicgas"] = "toxic"
CHEATS["nuke"] = "nuke"
CHEATS["nuclear"] = "nuke"
CHEATS["recruit"] = "recruit"

# check the longest words first (so "firesword" does not count as "sword")
CHEAT_ORDER = sorted(CHEATS.keys(), key=len, reverse=True)
TYPED_LENGTH = len(CHEAT_ORDER[0])

# ---------- sound ----------
def saw_wave(freq, t):
    return 2.0 * ((freq * t) % 1.0) - 1.0


def make_guitar_sound():
    setup = pygame.mixer.get_init()
    if setup is None:
        return None

    rate = setup[0]
    sample_format = setup[1]
    channels = setup[2]
    if sample_format != -16:
        return None

    samples = array.array("h")
    total = int(rate * GUITAR_SECONDS)
    for i in range(total):
        t = i / rate

        # three notes played together = a power chord
        wave = saw_wave(110, t) + saw_wave(165, t) + saw_wave(220, t)

        # distortion: chop the top off the wave
        wave = max(-1.0, min(1.0, wave))

        # quick start, then fade out
        attack = min(1.0, t * 400.0)
        fade = math.exp(-6.0 * t)
        sample = int(wave * attack * fade * 18000)

        samples.append(sample)
        if channels == 2:
            samples.append(sample)

    return pygame.mixer.Sound(buffer=samples.tobytes())


try:
    guitar_sound = make_guitar_sound()
except Exception:
    guitar_sound = None


def play_guitar_sound():
    if guitar_sound is None:
        return
    try:
        guitar_sound.play()
    except Exception:
        pass


# ---------- game data ----------
# the player is a Rect, so player_rect.x, .y, .bottom and so on all work
player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)

# coins and pickups are Rects too
coins = []
pickups = []

# enemies, bosses, bullets and weapons on the ground are dictionaries
enemies = []
bosses = []
bullets = []
weapon_items = []

# toxic gas clouds on the ground, and the bosses you recruited
clouds = []
allies = []

# things that reset every new run (reset_game fills it in)
state = {}

# things that are NOT reset when you die, they last until you close the game
permanent = {}
permanent["one_piece"] = False
permanent["typed"] = ""

# the toxic gas picture is made once (a see-through green cloud)
toxic_surface = pygame.Surface((TOXIC_WIDTH, TOXIC_HEIGHT), pygame.SRCALPHA)
pygame.draw.ellipse(toxic_surface, (60, 200, 60, 110), (0, 0, TOXIC_WIDTH, TOXIC_HEIGHT))
pygame.draw.ellipse(toxic_surface, (120, 255, 90, 90), (20, 14, TOXIC_WIDTH - 40, TOXIC_HEIGHT - 28))


# ---------- helpers that build things ----------
def make_coin(x):
    return pygame.Rect(x, ITEM_Y, ITEM_SIZE, ITEM_SIZE)


def make_pickup(x):
    return pygame.Rect(x, ITEM_Y, ITEM_SIZE, ITEM_SIZE)


def make_weapon_item(x, key):
    item = {}
    item["rect"] = pygame.Rect(x, WEAPON_ITEM_Y, WEAPON_ITEM_WIDTH, WEAPON_ITEM_HEIGHT)
    item["key"] = key
    return item


def make_enemy(x, left, right, kind, direction):
    speed = 2
    hits_needed = 1
    color = ENEMY_RED
    if kind == "tough":
        speed = 3
        hits_needed = 2
        color = ENEMY_PURPLE

    enemy = {}
    enemy["rect"] = pygame.Rect(x, ENEMY_Y, ENEMY_SIZE, ENEMY_SIZE)
    enemy["speed"] = speed
    enemy["dir"] = direction
    enemy["left"] = left
    enemy["right"] = right
    enemy["hits"] = 0
    enemy["hits_needed"] = hits_needed
    enemy["color"] = color
    return enemy


def make_boss(x, level):
    boss = {}
    boss["rect"] = pygame.Rect(x, BOSS_Y, BOSS_SIZE, BOSS_SIZE)
    boss["health"] = BOSS_HEALTH
    boss["level"] = level
    return boss


def make_ally(x):
    ally = {}
    ally["rect"] = pygame.Rect(x, BOSS_Y, BOSS_SIZE, BOSS_SIZE)
    ally["hit_timer"] = 0
    return ally


def reset_game():
    player_rect.x = 50
    player_rect.bottom = GROUND_Y

    state["vel_y"] = 0
    state["on_ground"] = True
    state["health"] = MAX_HEALTH
    state["invincible"] = 0
    state["score"] = 0
    state["world_end"] = START_WORLD_END
    state["game_over"] = False
    state["tick"] = 0
    state["facing"] = 1

    # weapons
    state["weapons"] = []
    state["current"] = 0
    state["shoot_timer"] = 0
    state["swing_timer"] = 0
    state["laser_timer"] = 0
    state["laser_dir"] = 1
    state["dragon_timer"] = 0

    # abilities
    state["abilities"] = []
    state["ability_index"] = 0
    state["shield_timer"] = 0
    state["nuke_timer"] = 0
    state["defeated_bosses"] = 0
    state["cooldowns"] = {}
    for key in ABILITIES:
        state["cooldowns"][key] = 0

    state["next_boss_level"] = BOSS_EVERY
    state["message"] = ""
    state["message_timer"] = 0

    # the One Piece stays with you forever (until the game is closed)
    if permanent["one_piece"]:
        give_weapon("onepiece")

    coins.clear()
    for x in [300, 500, 700, 900, 1100]:
        coins.append(make_coin(x))

    pickups.clear()
    for x in [650, 1050]:
        pickups.append(make_pickup(x))

    weapon_items.clear()
    weapon_items.append(make_weapon_item(200, "pistol"))
    weapon_items.append(make_weapon_item(950, "sword"))

    enemies.clear()
    enemies.append(make_enemy(400, 350, 550, "walker", 1))
    enemies.append(make_enemy(800, 750, 950, "walker", 1))
    enemies.append(make_enemy(1200, 1150, 1400, "tough", -1))

    bosses.clear()
    bullets.clear()
    clouds.clear()
    allies.clear()


# ---------- small helpers ----------
def show_message(text):
    state["message"] = text
    state["message_timer"] = MESSAGE_FRAMES


def hurt_player(amount):
    # the shield blocks all damage
    if state["shield_timer"] > 0:
        return

    state["health"] -= amount
    state["invincible"] = INVINCIBLE_FRAMES


def kill_enemy(enemy):
    enemies.remove(enemy)
    state["score"] += 2


def kill_boss(boss):
    bosses.remove(boss)
    state["score"] += BOSS_POINTS
    state["defeated_bosses"] += 1
    message = "BOSS DEFEATED!  +" + str(BOSS_POINTS)

    # some bosses give you a new ability
    level = boss["level"]
    if level in ABILITY_REWARDS:
        key = ABILITY_REWARDS[level]
        give_ability(key)
        message = "BOSS DEFEATED!  New ability: " + ABILITIES[key]["label"] + "  (Z)"

    show_message(message)


def damage_enemy(enemy, amount):
    enemy["hits"] += amount
    if enemy["hits"] >= enemy["hits_needed"]:
        kill_enemy(enemy)


def damage_boss(boss, amount):
    boss["health"] -= amount
    if boss["health"] <= 0:
        kill_boss(boss)


# ---------- weapon inventory ----------
def current_weapon():
    if len(state["weapons"]) == 0:
        return None
    return WEAPONS[state["weapons"][state["current"]]]


def equip_weapon(key):
    state["current"] = state["weapons"].index(key)


def give_weapon(key):
    # returns True if it is a new weapon, False if you already had it
    if key in state["weapons"]:
        return False
    state["weapons"].append(key)
    equip_weapon(key)
    return True


def switch_weapon():
    if len(state["weapons"]) == 0:
        return
    state["current"] = (state["current"] + 1) % len(state["weapons"])
    show_message("Weapon: " + current_weapon()["label"])


def unlock_one_piece():
    already = permanent["one_piece"]
    permanent["one_piece"] = True
    give_weapon("onepiece")
    equip_weapon("onepiece")
    if not already:
        show_message("ONE PIECE UNLOCKED!  Press X to fire")


# ---------- abilities ----------
def current_ability():
    if len(state["abilities"]) == 0:
        return None
    return state["abilities"][state["ability_index"]]


def select_ability(key):
    state["ability_index"] = state["abilities"].index(key)


def give_ability(key):
    # returns True if it is a new ability, False if you already had it
    if key in state["abilities"]:
        return False
    state["abilities"].append(key)
    select_ability(key)
    return True


def switch_ability():
    if len(state["abilities"]) == 0:
        show_message("No abilities yet - defeat a boss!")
        return
    state["ability_index"] = (state["ability_index"] + 1) % len(state["abilities"])
    show_message("Ability: " + ABILITIES[current_ability()]["label"])


def give_cheat_ability(key):
    give_ability(key)
    select_ability(key)
    message = "CHEAT: " + ABILITIES[key]["label"] + " ability added!"

    # recruiting needs defeated bosses, so make sure there are some
    if key == "recruit":
        state["defeated_bosses"] = max(state["defeated_bosses"], MAX_ALLIES)
        message = "CHEAT: RECRUIT added!  " + str(MAX_ALLIES) + " bosses ready to recruit"

    show_message(message)


def give_cheat(key):
    if key in ABILITIES:
        give_cheat_ability(key)
        return

    if key == "onepiece":
        unlock_one_piece()
        return

    give_weapon(key)
    equip_weapon(key)
    show_message("CHEAT: " + WEAPONS[key]["label"] + " added!")


def letter_continues_cheat(letter):
    # True if this letter looks like part of a cheat code being typed
    typed = permanent["typed"] + letter
    for start in range(len(typed) - 1):
        tail = typed[start:]
        for code in CHEAT_ORDER:
            if code.startswith(tail):
                return True
    return False


def handle_typing(event):
    if event.type != pygame.KEYDOWN:
        return

    # keep only the last few letters that were typed
    typed = permanent["typed"] + event.unicode.lower()
    permanent["typed"] = typed[-TYPED_LENGTH:]

    for code in CHEAT_ORDER:
        if permanent["typed"].endswith(code):
            permanent["typed"] = ""
            give_cheat(CHEATS[code])
            return


def pick_up_weapon(item):
    weapon_items.remove(item)
    key = item["key"]
    if give_weapon(key):
        show_message("Picked up " + WEAPONS[key]["label"] + "!  L = switch")
    else:
        state["score"] += 1


def collect_weapons():
    for item in weapon_items:
        if player_rect.colliderect(item["rect"]):
            pick_up_weapon(item)
            return


# ---------- firing weapons ----------
def muzzle_x(length):
    if state["facing"] == 1:
        return player_rect.right + length
    return player_rect.left - length


def add_bullet(start_x, center_y, width, height, speed, vy, damage, life, kind):
    x = start_x
    if state["facing"] == -1:
        x = start_x - width

    bullet = {}
    bullet["rect"] = pygame.Rect(x, center_y - height // 2, width, height)
    bullet["vx"] = speed * state["facing"]
    bullet["vy"] = vy
    bullet["damage"] = damage
    bullet["life"] = life
    bullet["kind"] = kind
    bullets.append(bullet)


def fire_projectile(weapon):
    width = weapon["size"]
    height = weapon["size"] // 2
    if weapon["kind"] == "skull":
        height = width

    start_x = muzzle_x(weapon["length"])
    center_y = player_rect.y + GUN_Y

    # a shotgun fires several pellets, each one going a little higher or lower
    for i in range(weapon["pellets"]):
        vy = i - weapon["pellets"] // 2
        add_bullet(start_x, center_y, width, height, weapon["speed"], vy, weapon["damage"], weapon["life"], weapon["kind"])

    state["shoot_timer"] = weapon["cooldown"]

    if weapon["key"] == "guitar":
        play_guitar_sound()


def fire_melee(weapon):
    reach = weapon["speed"]
    x = player_rect.right
    if state["facing"] == -1:
        x = player_rect.left - reach
    hitbox = pygame.Rect(x, player_rect.y - 5, reach, PLAYER_SIZE + 10)

    # [:] makes a copy of the list, so we can remove enemies safely
    for enemy in enemies[:]:
        if hitbox.colliderect(enemy["rect"]):
            damage_enemy(enemy, weapon["damage"])

    for boss in bosses[:]:
        if hitbox.colliderect(boss["rect"]):
            damage_boss(boss, weapon["damage"])

    state["swing_timer"] = weapon["life"]
    state["shoot_timer"] = weapon["cooldown"]


def fire_laser(weapon):
    state["laser_timer"] = LASER_FRAMES
    state["laser_dir"] = state["facing"]
    state["shoot_timer"] = weapon["cooldown"]


def start_dragon():
    state["dragon_timer"] = DRAGON_FRAMES
    state["vel_y"] = 0
    state["shoot_timer"] = 10
    show_message("DRAGON MODE!  UP/DOWN = fly, X = fire")


def fire_dragon_breath():
    start_x = muzzle_x(DRAGON_MOUTH)
    center_y = player_rect.centery - 6
    add_bullet(start_x, center_y, DRAGON_FIRE_WIDTH, DRAGON_FIRE_HEIGHT, DRAGON_FIRE_SPEED, 0, DRAGON_FIRE_DAMAGE, DRAGON_FIRE_LIFE, "fire")
    state["shoot_timer"] = DRAGON_FIRE_COOLDOWN


def update_weapon():
    if state["shoot_timer"] > 0:
        state["shoot_timer"] -= 1
    if state["swing_timer"] > 0:
        state["swing_timer"] -= 1

    keys = pygame.key.get_pressed()
    if not keys[pygame.K_x]:
        return
    if state["shoot_timer"] > 0:
        return

    # as a dragon, X always breathes fire
    if state["dragon_timer"] > 0:
        fire_dragon_breath()
        return

    weapon = current_weapon()
    if weapon is None:
        return

    kind = weapon["kind"]
    if kind == "gun" or kind == "skull":
        fire_projectile(weapon)
    elif kind == "melee":
        fire_melee(weapon)
    elif kind == "laser":
        fire_laser(weapon)
    elif kind == "dragon":
        start_dragon()


def bullet_hit_something(bullet):
    for enemy in enemies:
        if bullet["rect"].colliderect(enemy["rect"]):
            damage_enemy(enemy, bullet["damage"])
            return True

    for boss in bosses:
        if bullet["rect"].colliderect(boss["rect"]):
            damage_boss(boss, bullet["damage"])
            return True

    return False


def update_bullets():
    for bullet in bullets[:]:
        bullet["rect"].x += bullet["vx"]
        bullet["rect"].y += bullet["vy"]
        bullet["life"] -= 1

        hit = bullet_hit_something(bullet)
        hit_ground = bullet["rect"].bottom > GROUND_Y
        if hit or hit_ground or bullet["life"] <= 0:
            bullets.remove(bullet)


def get_laser_rect():
    y = player_rect.y + GUN_Y - LASER_THICKNESS // 2
    if state["laser_dir"] == 1:
        x = player_rect.right + GUN_LENGTH
    else:
        x = player_rect.left - GUN_LENGTH - LASER_LENGTH
    return pygame.Rect(x, y, LASER_LENGTH, LASER_THICKNESS)


def update_laser():
    if state["laser_timer"] <= 0:
        return

    state["laser_timer"] -= 1
    beam = get_laser_rect()

    # the laser kills anything it touches, in one hit
    for enemy in enemies[:]:
        if beam.colliderect(enemy["rect"]):
            kill_enemy(enemy)

    for boss in bosses[:]:
        if beam.colliderect(boss["rect"]):
            kill_boss(boss)


def update_dragon_timer():
    if state["dragon_timer"] <= 0:
        return

    state["dragon_timer"] -= 1
    if state["dragon_timer"] == 0:
        state["shoot_timer"] = DRAGON_COOLDOWN
        show_message("Dragon mode is over")


# ---------- using abilities ----------
def cast_fireball():
    start_x = muzzle_x(20)
    center_y = player_rect.y + GUN_Y
    add_bullet(start_x, center_y, FIREBALL_SIZE, FIREBALL_SIZE, FIREBALL_SPEED, 0, FIREBALL_DAMAGE, FIREBALL_LIFE, "fireball")
    return True


def cast_shield():
    state["shield_timer"] = SHIELD_FRAMES
    show_message("SHIELD ON!  Nothing can hurt you")
    return True


def cast_toxic():
    area = pygame.Rect(0, 0, TOXIC_WIDTH, TOXIC_HEIGHT)
    area.centerx = player_rect.centerx
    area.bottom = GROUND_Y

    cloud = {}
    cloud["rect"] = area
    cloud["life"] = TOXIC_FRAMES
    clouds.append(cloud)
    show_message("TOXIC GAS!")
    return True


def cast_nuke():
    show_message("NUKE!")

    # everything you can see on the screen gets destroyed
    camera_x = player_rect.x - CAMERA_OFFSET
    view = pygame.Rect(camera_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    for enemy in enemies[:]:
        if view.colliderect(enemy["rect"]):
            kill_enemy(enemy)

    for boss in bosses[:]:
        if view.colliderect(boss["rect"]):
            kill_boss(boss)

    state["nuke_timer"] = NUKE_FRAMES
    return True


def cast_recruit():
    if state["defeated_bosses"] <= 0:
        show_message("No defeated bosses to recruit yet!")
        return False
    if len(allies) >= MAX_ALLIES:
        show_message("Recruit limit reached (" + str(MAX_ALLIES) + ")")
        return False

    state["defeated_bosses"] -= 1
    allies.append(make_ally(player_rect.x - 100))
    show_message("Boss recruited!  Allies: " + str(len(allies)) + "/" + str(MAX_ALLIES))
    return True


def use_ability():
    key = current_ability()
    if key is None:
        show_message("No abilities yet - defeat a boss!")
        return
    if state["cooldowns"][key] > 0:
        show_message(ABILITIES[key]["label"] + " is recharging...")
        return

    used = False
    if key == "fireball":
        used = cast_fireball()
    elif key == "shield":
        used = cast_shield()
    elif key == "toxic":
        used = cast_toxic()
    elif key == "nuke":
        used = cast_nuke()
    elif key == "recruit":
        used = cast_recruit()

    if used:
        state["cooldowns"][key] = ABILITIES[key]["cooldown"]


def update_ability_timers():
    for key in state["cooldowns"]:
        if state["cooldowns"][key] > 0:
            state["cooldowns"][key] -= 1

    if state["shield_timer"] > 0:
        state["shield_timer"] -= 1
        if state["shield_timer"] == 0:
            show_message("Shield is down")

    if state["nuke_timer"] > 0:
        state["nuke_timer"] -= 1


def poison_things_in(area):
    for enemy in enemies[:]:
        if area.colliderect(enemy["rect"]):
            damage_enemy(enemy, 1)

    for boss in bosses[:]:
        if area.colliderect(boss["rect"]):
            damage_boss(boss, 1)


def update_clouds():
    for cloud in clouds[:]:
        cloud["life"] -= 1
        if cloud["life"] <= 0:
            clouds.remove(cloud)
        elif state["tick"] % TOXIC_TICK == 0:
            poison_things_in(cloud["rect"])


def ally_attack(ally):
    if ally["hit_timer"] > 0:
        ally["hit_timer"] -= 1
        return

    rect = ally["rect"]
    hit_something = False

    for enemy in enemies[:]:
        if rect.colliderect(enemy["rect"]):
            damage_enemy(enemy, ALLY_DAMAGE)
            hit_something = True

    for boss in bosses[:]:
        if rect.colliderect(boss["rect"]):
            damage_boss(boss, ALLY_BOSS_DAMAGE)
            hit_something = True

    if hit_something:
        ally["hit_timer"] = ALLY_HIT_FRAMES


def update_allies():
    for i in range(len(allies)):
        rect = allies[i]["rect"]

        # stand behind the player, each ally a bit further back
        target_x = player_rect.centerx - state["facing"] * (100 + i * 90) - BOSS_SIZE // 2
        if rect.x < target_x - ALLY_SPEED:
            rect.x += ALLY_SPEED
        elif rect.x > target_x + ALLY_SPEED:
            rect.x -= ALLY_SPEED

        # if an ally gets lost far away, bring it back
        if abs(rect.x - player_rect.x) > 600:
            rect.x = target_x

        ally_attack(allies[i])


# ---------- movement ----------
def jump_and_fall(keys):
    if keys[pygame.K_SPACE] and state["on_ground"]:
        state["vel_y"] = JUMP_POWER
        state["on_ground"] = False

    state["vel_y"] += GRAVITY
    player_rect.y += state["vel_y"]

    if player_rect.bottom >= GROUND_Y:
        player_rect.bottom = GROUND_Y
        state["vel_y"] = 0
        state["on_ground"] = True


def fly(keys):
    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
        player_rect.y -= DRAGON_FLY_SPEED
    if keys[pygame.K_DOWN]:
        player_rect.y += DRAGON_FLY_SPEED

    if player_rect.y < 0:
        player_rect.y = 0
    if player_rect.bottom > GROUND_Y:
        player_rect.bottom = GROUND_Y

    state["vel_y"] = 0
    state["on_ground"] = player_rect.bottom >= GROUND_Y


def update_player():
    keys = pygame.key.get_pressed()

    speed = PLAYER_SPEED
    if state["dragon_timer"] > 0:
        speed = DRAGON_SPEED

    if keys[pygame.K_LEFT]:
        player_rect.x -= speed
        state["facing"] = -1
    if keys[pygame.K_RIGHT]:
        player_rect.x += speed
        state["facing"] = 1
    if player_rect.x < 0:
        player_rect.x = 0

    if state["dragon_timer"] > 0:
        fly(keys)
    else:
        jump_and_fall(keys)

    if state["invincible"] > 0:
        state["invincible"] -= 1


# ---------- world ----------
def spawn_chunk(start):
    coin_x = start + random.randint(50, CHUNK_WIDTH - 50)
    coins.append(make_coin(coin_x))

    if random.randint(1, 3) == 1:
        pickup_x = start + random.randint(50, CHUNK_WIDTH - 50)
        pickups.append(make_pickup(pickup_x))

    if random.randint(1, WEAPON_CHANCE) == 1:
        weapon_x = start + random.randint(50, CHUNK_WIDTH - 50)
        weapon_key = random.choice(WEAPON_SPAWN_LIST)
        weapon_items.append(make_weapon_item(weapon_x, weapon_key))

    if random.randint(1, 2) == 1:
        left = start + 50
        right = start + CHUNK_WIDTH - 90
        kind = "walker"
        if random.randint(1, 3) == 1:
            kind = "tough"
        enemies.append(make_enemy(left, left, right, kind, 1))


def spawn_world():
    while player_rect.x + LOOKAHEAD > state["world_end"]:
        spawn_chunk(state["world_end"])
        state["world_end"] += CHUNK_WIDTH


def update_enemies():
    for enemy in enemies:
        rect = enemy["rect"]
        rect.x += enemy["speed"] * enemy["dir"]
        if rect.x <= enemy["left"]:
            enemy["dir"] = 1
        if rect.x >= enemy["right"]:
            enemy["dir"] = -1


def update_bosses():
    for boss in bosses:
        rect = boss["rect"]
        if rect.centerx > player_rect.centerx:
            rect.x -= BOSS_SPEED
        elif rect.centerx < player_rect.centerx:
            rect.x += BOSS_SPEED


def check_boss_spawn():
    # only one boss at a time
    if len(bosses) > 0:
        return
    if state["score"] < state["next_boss_level"]:
        return

    level = state["next_boss_level"]
    bosses.append(make_boss(player_rect.x + BOSS_SPAWN_DISTANCE, level))

    # the next boss is 50 points higher (no boss level is ever skipped)
    state["next_boss_level"] = level + BOSS_EVERY

    message = "BOSS INCOMING!"
    if len(state["weapons"]) == 0:
        give_weapon("pistol")
        message = "BOSS INCOMING!  Here is a pistol, press X"
    show_message(message)


def check_one_piece_score():
    if state["score"] >= ONE_PIECE_SCORE and not permanent["one_piece"]:
        unlock_one_piece()


def collect_coins():
    hit = player_rect.collidelist(coins)
    if hit != -1:
        coins.pop(hit)
        state["score"] += 1


def collect_pickups():
    hit = player_rect.collidelist(pickups)
    if hit != -1:
        pickups.pop(hit)
        state["health"] = min(MAX_HEALTH, state["health"] + HEAL_AMOUNT)


def stomp_enemy(enemy):
    damage_enemy(enemy, 1)

    # sit the player on top of the enemy, then bounce
    player_rect.bottom = enemy["rect"].top
    state["vel_y"] = JUMP_POWER // 2


def touch_enemy(enemy):
    # where were the player's feet on the last frame?
    last_bottom = player_rect.bottom - state["vel_y"]
    is_falling = state["vel_y"] > 0
    landed_on_top = is_falling and last_bottom <= enemy["rect"].top + STOMP_MARGIN

    if landed_on_top:
        stomp_enemy(enemy)
    elif state["invincible"] == 0:
        hurt_player(ENEMY_DAMAGE)


def check_enemies():
    for enemy in enemies:
        if player_rect.colliderect(enemy["rect"]):
            touch_enemy(enemy)
            return


def check_bosses():
    # you can not stomp a boss, touching it always hurts
    for boss in bosses:
        touching = player_rect.colliderect(boss["rect"])
        if touching and state["invincible"] == 0:
            hurt_player(BOSS_DAMAGE)


def update_game():
    state["tick"] += 1

    update_player()
    update_weapon()
    update_dragon_timer()
    update_ability_timers()
    spawn_world()
    update_enemies()
    update_bosses()
    update_bullets()
    update_laser()
    update_clouds()
    update_allies()
    collect_coins()
    collect_pickups()
    collect_weapons()
    check_enemies()
    check_bosses()
    check_boss_spawn()
    check_one_piece_score()

    if state["message_timer"] > 0:
        state["message_timer"] -= 1

    if state["health"] <= 0:
        state["health"] = 0
        state["game_over"] = True


# ---------- drawing functions ----------
def draw_stick_figure(color, x, y, w, h, thickness=3):
    head_radius = w // 3
    head_x = x + w // 2
    head_y = y + head_radius
    pygame.draw.circle(screen, color, (head_x, head_y), head_radius, thickness)

    body_top = head_y + head_radius
    body_bottom = y + h - (h // 4)
    pygame.draw.line(screen, color, (head_x, body_top), (head_x, body_bottom), thickness)

    arm_y = body_top + (body_bottom - body_top) // 3
    pygame.draw.line(screen, color, (x, arm_y), (x + w, arm_y), thickness)

    feet_y = y + h
    pygame.draw.line(screen, color, (head_x, body_bottom), (x, feet_y), thickness)
    pygame.draw.line(screen, color, (head_x, body_bottom), (x + w, feet_y), thickness)


def draw_weapon_items(camera_x):
    for item in weapon_items:
        rect = item["rect"]
        weapon = WEAPONS[item["key"]]
        screen_x = rect.x - camera_x
        box = (screen_x, rect.y, rect.width, rect.height)
        pygame.draw.rect(screen, weapon["color"], box)
        pygame.draw.rect(screen, BLACK, box, 2)

        label = labels[item["key"]]
        label_pos = (screen_x + rect.width // 2, rect.y - 3)
        screen.blit(label, label.get_rect(midbottom=label_pos))


def draw_world(camera_x):
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GROUND_GREEN, (0, GROUND_Y, SCREEN_WIDTH, GROUND_HEIGHT))

    for coin in coins:
        center = (coin.centerx - camera_x, coin.centery)
        pygame.draw.circle(screen, COIN_YELLOW, center, ITEM_SIZE // 2)

    for pickup in pickups:
        center = (pickup.centerx - camera_x, pickup.centery)
        pygame.draw.circle(screen, HEALTH_GREEN, center, ITEM_SIZE // 2)
        screen.blit(plus_text, plus_text.get_rect(center=center))

    draw_weapon_items(camera_x)
    draw_clouds(camera_x)

    for enemy in enemies:
        rect = enemy["rect"]
        draw_stick_figure(enemy["color"], rect.x - camera_x, rect.y, rect.width, rect.height)


def draw_bosses(camera_x):
    for boss in bosses:
        rect = boss["rect"]
        screen_x = rect.x - camera_x
        draw_stick_figure(BOSS_COLOR, screen_x, rect.y, rect.width, rect.height, 6)

        # boss health bar above its head
        level_text = tiny_font.render("BOSS " + str(boss["level"]), True, BLACK)
        level_pos = (screen_x + rect.width // 2, rect.y - 18)
        screen.blit(level_text, level_text.get_rect(midbottom=level_pos))

        bar = pygame.Rect(screen_x, rect.y - 16, rect.width, 8)
        fill_width = int(bar.width * boss["health"] / BOSS_HEALTH)
        pygame.draw.rect(screen, HEALTH_BG, bar)
        pygame.draw.rect(screen, HEALTH_RED, (bar.x, bar.y, fill_width, bar.height))
        pygame.draw.rect(screen, BLACK, bar, 2)


def draw_skull(rect, camera_x):
    center_x = rect.centerx - camera_x
    center_y = rect.centery
    radius = rect.width // 2
    eye = radius // 3

    pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 1)
    pygame.draw.circle(screen, BLACK, (center_x - eye - 1, center_y - 1), 2)
    pygame.draw.circle(screen, BLACK, (center_x + eye + 1, center_y - 1), 2)
    mouth_y = center_y + radius // 2
    pygame.draw.line(screen, BLACK, (center_x - eye, mouth_y), (center_x + eye, mouth_y), 2)


def draw_flame(rect, camera_x):
    x = rect.x - camera_x
    outer = (x, rect.y, rect.width, rect.height)
    inner = (x + rect.width // 4, rect.y + rect.height // 4, rect.width // 2, rect.height // 2)
    pygame.draw.ellipse(screen, FIRE_ORANGE, outer)
    pygame.draw.ellipse(screen, YELLOW, inner)


def draw_bullets(camera_x):
    for bullet in bullets:
        rect = bullet["rect"]
        if bullet["kind"] == "skull":
            draw_skull(rect, camera_x)
        elif bullet["kind"] == "fire":
            draw_flame(rect, camera_x)
        elif bullet["kind"] == "fireball":
            draw_fireball(rect, camera_x)
        else:
            pygame.draw.rect(screen, BULLET_COLOR, (rect.x - camera_x, rect.y, rect.width, rect.height))


def draw_laser(camera_x):
    if state["laser_timer"] <= 0:
        return

    beam = get_laser_rect()
    pygame.draw.rect(screen, LASER_RED, (beam.x - camera_x, beam.y, beam.width, beam.height))

    # a lighter stripe in the middle makes it glow
    core_height = LASER_THICKNESS // 3
    core_y = beam.centery - core_height // 2
    pygame.draw.rect(screen, LASER_CORE, (beam.x - camera_x, core_y, beam.width, core_height))


def hand_position(camera_x):
    hand_x = player_rect.x - camera_x
    if state["facing"] == 1:
        hand_x = hand_x + PLAYER_SIZE
    hand_y = player_rect.y + GUN_Y
    return hand_x, hand_y


def draw_gun(camera_x, weapon):
    thickness = 6
    if weapon["kind"] == "laser":
        thickness = 10

    length = weapon["length"]
    hand_x, hand_y = hand_position(camera_x)
    gun_x = hand_x
    if state["facing"] == -1:
        gun_x = hand_x - length
    pygame.draw.rect(screen, weapon["color"], (gun_x, hand_y - thickness // 2, length, thickness))


def draw_sword(camera_x, weapon):
    facing = state["facing"]
    hand_x, hand_y = hand_position(camera_x)
    reach = weapon["speed"]

    # resting: the blade points up.  swinging: the blade sweeps from high to low
    tip_x = hand_x + facing * 12
    tip_y = hand_y - reach // 2
    if state["swing_timer"] > 0:
        progress = weapon["life"] - state["swing_timer"]
        tip_x = hand_x + facing * reach
        tip_y = hand_y - 30 + progress * 60 // weapon["life"]

    if weapon["key"] == "firesword":
        pygame.draw.line(screen, FIRE_ORANGE, (hand_x, hand_y), (tip_x, tip_y), 9)
        pygame.draw.line(screen, YELLOW, (hand_x, hand_y), (tip_x, tip_y), 3)
        pygame.draw.circle(screen, YELLOW, (tip_x, tip_y), 5 + state["tick"] % 3 * 2)
    else:
        pygame.draw.line(screen, weapon["color"], (hand_x, hand_y), (tip_x, tip_y), 4)


def draw_guitar(camera_x, weapon):
    facing = state["facing"]
    hand_x, hand_y = hand_position(camera_x)
    body_x = hand_x + facing * 8
    neck_x = hand_x + facing * weapon["length"]

    pygame.draw.circle(screen, weapon["color"], (body_x, hand_y + 4), 8)
    pygame.draw.line(screen, BROWN, (body_x, hand_y + 4), (neck_x, hand_y - 8), 3)


def draw_held_weapon(camera_x):
    weapon = current_weapon()
    if weapon is None:
        return

    if weapon["kind"] == "melee":
        draw_sword(camera_x, weapon)
    elif weapon["kind"] == "skull":
        draw_guitar(camera_x, weapon)
    else:
        draw_gun(camera_x, weapon)


def draw_dragon(camera_x):
    facing = state["facing"]
    cx = player_rect.centerx - camera_x
    cy = player_rect.centery

    # the wing flaps up and down
    wing_height = 40
    if (state["tick"] // 8) % 2 == 0:
        wing_height = 20

    # tail
    tail_start = cx - facing * 30
    tail_end = cx - facing * 62
    tail = [(tail_start, cy - 6), (tail_start, cy + 6), (tail_end, cy + 16)]
    pygame.draw.polygon(screen, DRAGON_GREEN, tail)

    # wing (behind the body)
    wing = [(cx - 18, cy - 12), (cx + 12, cy - 12), (cx - facing * 8, cy - 12 - wing_height)]
    pygame.draw.polygon(screen, DRAGON_DARK, wing)

    # body and belly
    pygame.draw.ellipse(screen, DRAGON_GREEN, (cx - 34, cy - 15, 68, 30))
    pygame.draw.ellipse(screen, DRAGON_BELLY, (cx - 26, cy - 2, 52, 14))

    # legs
    pygame.draw.line(screen, DRAGON_DARK, (cx - 14, cy + 12), (cx - 14, cy + 22), 4)
    pygame.draw.line(screen, DRAGON_DARK, (cx + 14, cy + 12), (cx + 14, cy + 22), 4)

    # head, snout, eye and horn
    head_x = cx + facing * 38
    pygame.draw.circle(screen, DRAGON_GREEN, (head_x, cy - 8), 13)
    pygame.draw.circle(screen, DRAGON_GREEN, (cx + facing * 50, cy - 5), 8)
    pygame.draw.circle(screen, WHITE, (head_x + facing * 2, cy - 12), 3)
    pygame.draw.circle(screen, BLACK, (head_x + facing * 3, cy - 12), 1)
    pygame.draw.line(screen, DRAGON_DARK, (head_x, cy - 18), (head_x - facing * 6, cy - 28), 3)


def draw_fireball(rect, camera_x):
    center = (rect.centerx - camera_x, rect.centery)
    radius = rect.width // 2
    flicker = state["tick"] % 3
    pygame.draw.circle(screen, FIREBALL_RED, center, radius)
    pygame.draw.circle(screen, FIRE_ORANGE, center, radius - 4)
    pygame.draw.circle(screen, YELLOW, center, radius // 2 + flicker)


def draw_clouds(camera_x):
    for cloud in clouds:
        rect = cloud["rect"]
        x = rect.x - camera_x
        screen.blit(toxic_surface, (x, rect.y))

        # bubbles that float up
        for i in range(5):
            bubble_x = x + 30 + i * 40
            rise = (state["tick"] * 2 + i * 23) % (rect.height - 30)
            bubble_y = rect.bottom - 15 - rise
            pygame.draw.circle(screen, TOXIC_LIGHT, (bubble_x, bubble_y), 5)


def draw_allies(camera_x):
    for ally in allies:
        rect = ally["rect"]
        screen_x = rect.x - camera_x
        draw_stick_figure(ALLY_BLUE, screen_x, rect.y, rect.width, rect.height, 6)

        label_pos = (screen_x + rect.width // 2, rect.y - 4)
        screen.blit(ally_label, ally_label.get_rect(midbottom=label_pos))


def draw_shield(camera_x):
    if state["shield_timer"] <= 0:
        return

    # blink when the shield is about to run out
    if state["shield_timer"] < 60 and state["tick"] % 10 < 5:
        return

    radius = 34
    if state["dragon_timer"] > 0:
        radius = 60

    center = (player_rect.centerx - camera_x, player_rect.centery)
    pygame.draw.circle(screen, SHIELD_CYAN, center, radius, 4)
    pygame.draw.circle(screen, SHIELD_LIGHT, center, radius - 6, 2)


def draw_nuke(camera_x):
    if state["nuke_timer"] <= 0:
        return

    progress = NUKE_FRAMES - state["nuke_timer"]

    # a bright white flash first, then a shockwave that grows
    if progress < 6:
        screen.fill(WHITE)
        return

    center = (player_rect.centerx - camera_x, player_rect.centery)
    radius = progress * 18
    pygame.draw.circle(screen, FIRE_ORANGE, center, radius, 14)
    pygame.draw.circle(screen, YELLOW, center, radius // 2, 8)


def draw_player_body(camera_x):
    if state["dragon_timer"] > 0:
        draw_dragon(camera_x)
        return

    draw_stick_figure(BLACK, player_rect.x - camera_x, player_rect.y, PLAYER_SIZE, PLAYER_SIZE)
    draw_held_weapon(camera_x)


def draw_player(camera_x):
    # blink while invincible (when the timer is 0 this is always true)
    if state["invincible"] % 10 < 5:
        draw_player_body(camera_x)

    draw_shield(camera_x)


def list_text(keys, table, chosen):
    # makes text like "PISTOL  [SHOTGUN]  RIFLE" (the chosen one is in brackets)
    text = ""
    for i in range(len(keys)):
        name = table[keys[i]]["label"]
        if i == chosen:
            name = "[" + name + "]"
        text = text + name + "  "
    return text


def draw_hud():
    score_text = font.render("Score: " + str(state["score"]), True, BLACK)
    screen.blit(score_text, (10, 10))

    bar = pygame.Rect(10, 50, 200, 20)
    fill_width = int(bar.width * state["health"] / MAX_HEALTH)
    pygame.draw.rect(screen, HEALTH_BG, bar)
    pygame.draw.rect(screen, HEALTH_RED, (bar.x, bar.y, fill_width, bar.height))
    pygame.draw.rect(screen, BLACK, bar, 2)

    # weapons, the one you are holding is in [brackets]
    names = list_text(state["weapons"], WEAPONS, state["current"])
    if names == "":
        names = "none (find one on the ground)"
    weapon_text = tiny_font.render("Weapons (L = switch, X = fire): " + names, True, BLACK)
    screen.blit(weapon_text, (10, 80))

    # abilities, the selected one is in [brackets]
    names = list_text(state["abilities"], ABILITIES, state["ability_index"])
    if names == "":
        names = "none (defeat a boss)"
    ability_text = tiny_font.render("Abilities (Q = switch, Z = use): " + names, True, BLACK)
    screen.blit(ability_text, (10, 98))

    # is the selected ability ready?
    key = current_ability()
    if key is not None:
        cooldown = state["cooldowns"][key]
        status = "READY"
        if cooldown > 0:
            status = "recharging " + str(cooldown // FPS + 1) + "s"

        icon = (10, 118, 14, 14)
        pygame.draw.rect(screen, ABILITIES[key]["color"], icon)
        pygame.draw.rect(screen, BLACK, icon, 2)
        status_text = small_font.render(ABILITIES[key]["label"] + ": " + status, True, BLACK)
        screen.blit(status_text, (30, 116))

    boss_text = small_font.render("Next boss at: " + str(state["next_boss_level"]), True, BLACK)
    screen.blit(boss_text, (10, 140))

    # things that are switched on right now
    effects = ""
    if state["dragon_timer"] > 0:
        effects = effects + "DRAGON " + str(state["dragon_timer"] // FPS + 1) + "s   "
    if state["shield_timer"] > 0:
        effects = effects + "SHIELD " + str(state["shield_timer"] // FPS + 1) + "s   "
    if effects != "":
        screen.blit(small_font.render(effects, True, BLACK), (10, 162))

    # recruiting info
    if "recruit" in state["abilities"] or len(allies) > 0:
        info = "Allies: " + str(len(allies)) + "/" + str(MAX_ALLIES) + "   Defeated bosses: " + str(state["defeated_bosses"])
        screen.blit(tiny_font.render(info, True, BLACK), (10, 184))


def draw_message():
    if state["message_timer"] <= 0:
        return
    text = font.render(state["message"], True, BLACK)
    screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 230)))


def draw_game_over():
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    box = pygame.Rect(0, 0, 400, 140)
    box.center = (center_x, center_y)
    pygame.draw.rect(screen, BLACK, box)

    over_text = big_font.render("GAME OVER", True, WHITE)
    restart_text = font.render("Press R to restart", True, WHITE)
    screen.blit(over_text, over_text.get_rect(center=(center_x, center_y - 25)))
    screen.blit(restart_text, restart_text.get_rect(center=(center_x, center_y + 30)))


# ---------- main loop ----------
def handle_events():
    # returns False when the window is closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # L switches weapon (but not when the L is part of a cheat code)
        pressed_l = event.type == pygame.KEYDOWN and event.key == pygame.K_l
        if pressed_l and not state["game_over"] and not letter_continues_cheat("l"):
            switch_weapon()

        # Q switches ability, Z uses the selected ability
        pressed_q = event.type == pygame.KEYDOWN and event.key == pygame.K_q
        if pressed_q and not state["game_over"]:
            switch_ability()

        pressed_z = event.type == pygame.KEYDOWN and event.key == pygame.K_z
        if pressed_z and not state["game_over"]:
            use_ability()

        handle_typing(event)

        pressed_r = event.type == pygame.KEYDOWN and event.key == pygame.K_r
        if pressed_r and state["game_over"]:
            reset_game()

    return True


def draw_frame():
    camera_x = player_rect.x - CAMERA_OFFSET

    draw_world(camera_x)
    draw_bosses(camera_x)
    draw_allies(camera_x)
    draw_bullets(camera_x)
    draw_laser(camera_x)
    draw_player(camera_x)
    draw_nuke(camera_x)
    draw_hud()
    draw_message()

    if state["game_over"]:
        draw_game_over()

    pygame.display.flip()


# the loop is "async" so the game can run in a web browser too (pygbag)
async def main():
    reset_game()
    running = True

    while running:
        running = handle_events()

        if not state["game_over"]:
            update_game()

        draw_frame()
        clock.tick(FPS)

        # gives the browser a moment to breathe (very important for the web version)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
