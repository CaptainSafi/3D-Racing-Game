from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, random, time, math

# =====================================================================================
# SECTION 1: GLOBAL STATE AND CONFIGURATION
# =====================================================================================

WIDTH, HEIGHT = 960, 540
ASPECT = WIDTH / HEIGHT
MENU, GAME, PAUSE, GAMEOVER = 0, 1, 2, 3
state = MENU
show_wiki = False
last_time = time.time()
dt = 0.0
player_speed = 20.0
base_speed = 20.0
left_lanes = [-10.0, -6.0, -2.0]
right_lanes = [2.0, 6.0, 10.0]
lanes = left_lanes + right_lanes
player_lane_index = 3
player_x = lanes[player_lane_index]
player_z = 0.0
player_y = 0.5
steer_target_x = player_x
steer_speed = 12.0
selected_vehicle_index = 0
player_invulnerability_timer = 0.0
road_width = 12.0
spawn_z = 150.0
remove_z = -40.0
ground_scroll = 0.0
time_of_day = 0.0
trees = []
spawn_tree_cooldown = 0.0
spawn_tree_interval = 0.3
obstacles = []
spawn_cooldown = 0.0
spawn_interval = 1.0
obstacle_base_speed = 10.0
powerups = []
powerup_spawn_cooldown = 5.0
powerup_spawn_interval = 7.0
speed_boost_active = False
speed_boost_timer = 0.0
speed_boost_duration = 4.0
speed_boost_amount = 12.0
score = 0
high_score = 0
lives = 3
max_lives = 5
fuel = 100.0
max_fuel = 100.0
fuel_decrease_base = 2.0
near_miss_combo = 0
god_mode_active = False
fuel_emergency_spawned = False
police_active = False
police = None
police_spawn_score = 750
police_chase_active = False
police_evasion_timer = 0.0
police_evasion_duration = 20.0
show_police_warning = False
police_warning_timer = 0.0
camera_shake = 0.0
random.seed(1234)

# =====================================================================================
# SECTION 2: DRAWING PRIMITIVES AND MODELS
# =====================================================================================

def draw_cube(w=1, h=1, d=1):
    hw, hh, hd = w / 2, h / 2, d / 2
    glBegin(GL_QUADS)
    glVertex3f(hw, -hh, -hd); glVertex3f(hw, hh, -hd); glVertex3f(hw, hh, hd); glVertex3f(hw, -hh, hd)
    glVertex3f(-hw, -hh, hd); glVertex3f(-hw, hh, hd); glVertex3f(-hw, hh, -hd); glVertex3f(-hw, -hh, -hd)
    glVertex3f(-hw, hh, -hd); glVertex3f(-hw, hh, hd); glVertex3f(hw, hh, hd); glVertex3f(hw, hh, -hd)
    glVertex3f(-hw, -hh, hd); glVertex3f(-hw, -hh, -hd); glVertex3f(hw, -hh, -hd); glVertex3f(hw, -hh, hd)
    glVertex3f(-hw, -hh, hd); glVertex3f(hw, -hh, hd); glVertex3f(hw, hh, hd); glVertex3f(-hw, hh, hd)
    glVertex3f(hw, -hh, -hd); glVertex3f(-hw, -hh, -hd); glVertex3f(-hw, hh, -hd); glVertex3f(hw, hh, -hd)
    glEnd()

def draw_car(body_color=(0.2, 0.7, 1.0)):
    glPushMatrix()
    glColor3f(*body_color)
    draw_cube(1.2, 0.6, 2.2)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0.55, -0.2)
    glColor3f(body_color[0] * 0.8, body_color[1] * 0.8, body_color[2] * 0.8)
    draw_cube(0.9, 0.5, 1.2)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    for sx in (-0.55, 0.55):
        for sz in (-0.85, 0.85):
            glPushMatrix(); glTranslatef(sx, -0.15, sz); draw_cube(0.4, 0.4, 0.4); glPopMatrix()

def draw_van(body_color=(0.8, 0.8, 0.8)):
    glPushMatrix()
    glColor3f(*body_color)
    draw_cube(1.3, 1.0, 2.5)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0.4, 0.5)
    glColor3f(body_color[0] * 0.8, body_color[1] * 0.8, body_color[2] * 0.8)
    draw_cube(1.1, 0.8, 1.0)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    for sx in (-0.6, 0.6):
        for sz in (-1.0, 1.0):
            glPushMatrix(); glTranslatef(sx, -0.35, sz); draw_cube(0.5, 0.5, 0.5); glPopMatrix()

def draw_sports_car(body_color=(0.9, 0.1, 0.1)):
    glPushMatrix()
    glColor3f(*body_color)
    draw_cube(1.4, 0.4, 2.5)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0.35, -0.3)
    glColor3f(body_color[0] * 0.8, body_color[1] * 0.8, body_color[2] * 0.8)
    draw_cube(1.0, 0.4, 1.4)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    for sx in (-0.65, 0.65):
        for sz in (-1.0, 0.9):
            glPushMatrix(); glTranslatef(sx, -0.1, sz); draw_cube(0.45, 0.45, 0.45); glPopMatrix()

def draw_motorcycle(body_color=(0.3, 0.3, 0.3)):
    glPushMatrix()
    glColor3f(*body_color)
    draw_cube(0.6, 0.5, 2.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0.7, -0.8)
    glColor3f(0.2, 0.2, 0.2)
    draw_cube(1.2, 0.1, 0.1)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    for sz in (-0.9, 0.9):
        glPushMatrix(); glTranslatef(0, -0.2, sz); draw_cube(0.2, 0.8, 0.8); glPopMatrix()

player_vehicles = [draw_car, draw_sports_car, draw_van, draw_motorcycle]
vehicle_names = ["Sedan", "Sports Car", "Van", "Motorcycle"]
vehicle_speeds = [20.0, 25.0, 15.0, 30.0]

# =====================================================================================
# SECTION 3: UI, HUD, AND TEXT RENDERING
# =====================================================================================

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(font, ord(character))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():
    draw_text(20, HEIGHT - 40, f"SCORE: {int(score)}")
    draw_text(20, HEIGHT - 70, f"LIVES: {lives}")
    if near_miss_combo > 1:
        draw_text(20, HEIGHT - 100, f"COMBO x{near_miss_combo}", color=(1, 1, 0))

    fuel_percentage = int((fuel / max_fuel) * 100)
    draw_text(WIDTH - 180, HEIGHT - 40, f"FUEL: {fuel_percentage}%")

    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIDTH, 0, HEIGHT); glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS); glVertex2f(WIDTH-180, HEIGHT-70); glVertex2f(WIDTH-30, HEIGHT-70); glVertex2f(WIDTH-30, HEIGHT-50); glVertex2f(WIDTH-180, HEIGHT-50); glEnd()
    fuel_width = (fuel / max_fuel) * 150
    glColor3f(0.9, 0.5, 0.0)
    glBegin(GL_QUADS); glVertex2f(WIDTH-180, HEIGHT-70); glVertex2f(WIDTH-180+fuel_width, HEIGHT-70); glVertex2f(WIDTH-180+fuel_width, HEIGHT-50); glVertex2f(WIDTH-180, HEIGHT-50); glEnd()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

    if state == MENU:
        draw_text(WIDTH / 2 - 100, HEIGHT / 2 + 50, "3D RACING GAME", font=GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(WIDTH / 2 - 80, HEIGHT / 2 + 10, "Press Enter to Start")
        draw_text(WIDTH / 2 - 120, HEIGHT - 40, f"HIGH SCORE: {high_score}")
    elif state == PAUSE:
        if show_wiki:
            draw_text(WIDTH/2 - 100, HEIGHT/2 + 80, "--- POWER-UP WIKI ---", font=GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(WIDTH/2 - 150, HEIGHT/2 + 40, "Fuel Can (Orange): Refills a portion of your fuel.")
            draw_text(WIDTH/2 - 150, HEIGHT/2 + 10, "Extra Life (Blue): Grants an extra life.")
            draw_text(WIDTH/2 - 150, HEIGHT/2 - 20, "Speed Boost (Green): Grants a temporary burst of speed.")
            draw_text(WIDTH/2 - 80, HEIGHT/2 - 70, "Press ESC to Return")
        else:
            draw_text(WIDTH/2 - 40, HEIGHT/2 + 80, "PAUSED", font=GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(WIDTH/2 - 120, HEIGHT/2 + 40, f"Current Vehicle: {vehicle_names[selected_vehicle_index]}")
            draw_text(WIDTH/2 - 100, HEIGHT/2 + 10, "Resume (Enter)")
            draw_text(WIDTH/2 - 100, HEIGHT/2 - 20, "Restart (R)")
            draw_text(WIDTH/2 - 100, HEIGHT/2 - 50, "Change Vehicle (C)")
            draw_text(WIDTH/2 - 100, HEIGHT/2 - 80, "Wiki (W)")
    elif state == GAMEOVER:
        draw_text(WIDTH / 2 - 70, HEIGHT / 2 + 20, "GAME OVER", font=GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(WIDTH / 2 - 90, HEIGHT / 2 - 20, "Press Enter to Restart")

    if show_police_warning:
        draw_text(WIDTH / 2 - 100, HEIGHT / 2, "Police are chasing you!", font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1, 0.2, 0.2))
    if police_chase_active:
        time_left = int(police_evasion_duration - police_evasion_timer)
        draw_text(WIDTH / 2 - 120, 50, f"EVADE THE POLICE: {time_left}s", font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1, 1, 0))
    if god_mode_active:
        draw_text(WIDTH / 2 - 80, HEIGHT - 40, "GOD MODE ACTIVE", color=(1, 0, 1))

# =====================================================================================
# SECTION 4: CORE GAME LOGIC AND WORLD SIMULATION
# =====================================================================================

def reset_game():
    global state, score, lives, fuel, player_x, player_lane_index, steer_target_x, obstacles, powerups, police, ground_scroll, player_speed, base_speed, police_chase_active, police_active, speed_boost_active, near_miss_combo, fuel_emergency_spawned, god_mode_active, time_of_day, high_score
    if score > high_score: high_score = int(score)
    score = 0
    lives = 3
    fuel = max_fuel
    player_lane_index = len(lanes) // 2
    player_x = lanes[player_lane_index]
    steer_target_x = player_x
    obstacles.clear(); powerups.clear(); trees.clear()
    police = None
    ground_scroll = 0
    base_speed = vehicle_speeds[selected_vehicle_index]
    player_speed = base_speed
    police_chase_active = False
    police_active = False
    speed_boost_active = False
    near_miss_combo = 0
    fuel_emergency_spawned = False
    god_mode_active = False
    time_of_day = 0.0

def check_collision(px, pz, ox, oz, p_width=1.2, p_depth=2.2, o_width=1.2, o_depth=2.2):
    return (abs(px - ox) * 2 < (p_width + o_width)) and (abs(pz - oz) * 2 < (p_depth + o_depth))

def update(dt):
    global state, score, lives, fuel, player_x, ground_scroll, player_speed, base_speed, spawn_cooldown, powerup_spawn_cooldown, speed_boost_active, speed_boost_timer, player_invulnerability_timer, police_active, police, police_chase_active, police_evasion_timer, show_police_warning, police_warning_timer, fuel_emergency_spawned, high_score, god_mode_active, time_of_day, camera_shake

    if state != GAME:
        camera_shake = 0
        return

    time_of_day += dt * 0.01
    player_invulnerability_timer = max(0, player_invulnerability_timer - dt)
    camera_shake = max(0, camera_shake - dt * 2.0)
    player_x += (steer_target_x - player_x) * steer_speed * dt
    score_multiplier = 1 + (near_miss_combo * 0.1)
    score += player_speed * dt * score_multiplier

    if not god_mode_active:
        fuel -= dt * (fuel_decrease_base + (player_speed - base_speed) * 0.1)
        fuel = max(0, fuel)
    if fuel <= 0:
        lives -= 1
        if lives > 0:
            fuel = max_fuel / 4
        else:
            state = GAMEOVER
            if score > high_score: high_score = int(score)

    ground_scroll = (ground_scroll + player_speed * dt) % 20.0

    if speed_boost_active:
        speed_boost_timer -= dt
        if speed_boost_timer <= 0:
            speed_boost_active = False
            player_speed = base_speed

    spawn_cooldown -= dt
    if spawn_cooldown < 0:
        spawn_cooldown = spawn_interval * (base_speed / player_speed)
        lane = random.choice(lanes)
        car_type = random.choice([draw_car, draw_van, draw_sports_car])
        obstacles.append({'x': lane, 'z': spawn_z, 'draw_func': car_type, 'speed': obstacle_base_speed + random.uniform(-2, 2), 'color': (random.random(), random.random(), random.random())})

    powerup_spawn_cooldown -= dt
    if powerup_spawn_cooldown < 0:
        powerup_spawn_cooldown = powerup_spawn_interval
        ptype = random.choice(['fuel', 'life', 'boost'])
        colors = {'fuel': (1,0.5,0), 'life': (0.2,0.7,1), 'boost': (0,1,0)}
        powerups.append({'x': random.choice(lanes), 'z': spawn_z, 'type': ptype, 'color': colors[ptype]})

    if fuel < 25 and not fuel_emergency_spawned:
        powerups.append({'x': random.choice(lanes), 'z': spawn_z / 2, 'type': 'fuel', 'color': (1,0.5,0)})
        fuel_emergency_spawned = True
    elif fuel > 30:
        fuel_emergency_spawned = False

    for obs in list(obstacles):
        if check_collision(player_x, player_z, obs['x'], obs['z']):
            if player_invulnerability_timer <= 0 and not god_mode_active:
                lives -= 1
                player_invulnerability_timer = 2.0
                camera_shake = 1.0
                if lives <= 0:
                    state = GAMEOVER
                    if score > high_score: high_score = int(score)
            obstacles.remove(obs)

    for p in list(powerups):
        if check_collision(player_x, player_z, p['x'], p['z'], o_width=1.5, o_depth=1.5):
            if p['type'] == 'fuel': fuel = min(max_fuel, fuel + 30)
            elif p['type'] == 'life': lives = min(max_lives, lives + 1)
            elif p['type'] == 'boost':
                speed_boost_active = True
                speed_boost_timer = speed_boost_duration
                player_speed += speed_boost_amount
            powerups.remove(p)

    if (score > police_spawn_score or police_active) and not police and not police_chase_active:
        police = {'x': player_x, 'z': player_z - 20, 'speed': player_speed * 1.1}
        police_chase_active = True
        show_police_warning = True
        police_warning_timer = 3.0
        police_evasion_timer = 0.0
    
    if show_police_warning:
        police_warning_timer -= dt
        if police_warning_timer <= 0: show_police_warning = False

    if police_chase_active and police:
        police_evasion_timer += dt
        target_x = player_x
        police['x'] += (target_x - police['x']) * (steer_speed / 2) * dt
        police['z'] += (police['speed'] - player_speed) * dt

        if police['z'] > player_z and check_collision(player_x, player_z, police['x'], police['z']):
            if not god_mode_active:
                lives -= 1
                if lives <= 0:
                    state = GAMEOVER
                    if score > high_score: high_score = int(score)
                police_chase_active = False
                police = None
                police_active = False
        
        if police_evasion_timer > police_evasion_duration:
            police_chase_active = False
            police = None
            police_active = False
            score += 2500

# =====================================================================================
# SECTION 5: MAIN RENDERING AND DISPLAY
# =====================================================================================
def draw_road():
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.25)
    glBegin(GL_QUADS); glVertex3f(-road_width, 0, 200); glVertex3f(road_width, 0, 200); glVertex3f(road_width, 0, -50); glVertex3f(-road_width, 0, -50); glEnd()
    glColor3f(0.8, 0.8, 0.8)
    for lane_x in lanes:
        if lane_x == 0: continue
        for z in range(-50, 200, 20):
            glPushMatrix(); glTranslatef(lane_x, 0.01, z - ground_scroll); draw_cube(0.2, 0.02, 5.0); glPopMatrix()
    glPopMatrix()

def draw_scenery(current_dt):
    global spawn_tree_cooldown
    spawn_tree_cooldown -= current_dt
    if spawn_tree_cooldown < 0:
        spawn_tree_cooldown = spawn_tree_interval
        side = random.choice([-1, 1])
        offset = random.uniform(5, 20)
        tree_x = (road_width * side) + (offset * side)
        trees.append({'x': tree_x, 'z': spawn_z})
    for tree in trees: tree['z'] -= player_speed * current_dt
    trees[:] = [t for t in trees if t['z'] > remove_z]
    for tree in trees:
        glPushMatrix(); glTranslatef(tree['x'], 1, tree['z']); glColor3f(0.5, 0.3, 0.1); draw_cube(1, 2, 1); glPopMatrix()
        glPushMatrix(); glTranslatef(tree['x'], 5, tree['z']); glColor3f(0.1, 0.5, 0.1); draw_cube(2, 6, 2); glPopMatrix()

def draw_obstacles(current_dt):
    for obs in obstacles:
        obs['z'] -= (player_speed - obs['speed']) * current_dt
        glPushMatrix(); glTranslatef(obs['x'], 0.5, obs['z']); obs['draw_func'](obs['color']); glPopMatrix()
    obstacles[:] = [o for o in obstacles if o['z'] > remove_z]

def draw_powerups(current_dt):
    for p in powerups:
        p['z'] -= player_speed * current_dt
        glPushMatrix(); glTranslatef(p['x'], 1.0, p['z']); glColor3f(*p['color']); draw_cube(1.5, 1.5, 1.5); glPopMatrix()
    powerups[:] = [p for p in powerups if p['z'] > remove_z]

def draw_police():
    if police:
        glPushMatrix(); glTranslatef(police['x'], 0.5, police['z']); draw_sports_car(body_color=(0,0,0.8)); glPopMatrix()

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    day_brightness = 0.5 + 0.5 * math.sin(time_of_day)
    bg_r, bg_g, bg_b = 0.4 * day_brightness, 0.6 * day_brightness, 0.9 * day_brightness
    glClearColor(bg_r, bg_g, bg_b, 1.0)
    
    shake_x = (random.random() - 0.5) * camera_shake
    shake_y = (random.random() - 0.5) * camera_shake
    gluPerspective(90, ASPECT, 1, 500)
    gluLookAt(player_x + shake_x, player_y + 8 + shake_y, player_z - 10, player_x, player_y, player_z + 10, 0, 1, 0)

    draw_road()
    draw_scenery(dt)
    draw_obstacles(dt)
    draw_powerups(dt)
    draw_police()
    
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    player_vehicles[selected_vehicle_index]()
    glPopMatrix()
    
    draw_hud()
    glutSwapBuffers()

# =====================================================================================
# SECTION 6: MAIN LOOP AND INPUT HANDLING
# =====================================================================================
def idle():
    global last_time, dt
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    if dt > 0.1: dt = 0.1
    update(dt)
    glutPostRedisplay()

def keyboard(key, x, y):
    global state, show_wiki, selected_vehicle_index, god_mode_active, police_active
    if state == MENU and key == b'\r':
        state = GAME
        reset_game()
    elif state == GAME and key == b'\x1b':
        state = PAUSE
    elif state == PAUSE:
        if key == b'\r': state = GAME
        elif key == b'r' or key == b'R': reset_game(); state = GAME
        elif key == b'c' or key == b'C':
            if not show_wiki: selected_vehicle_index = (selected_vehicle_index + 1) % len(player_vehicles)
        elif key == b'w' or key == b'W': show_wiki = True
        elif key == b'\x1b': show_wiki = False; state = GAME
    elif state == GAMEOVER and key == b'\r':
        reset_game()
        state = MENU

    if state == GAME:
        if key == b'c' or key == b'C': god_mode_active = not god_mode_active
        if key == b'p' or key == b'P': police_active = not police_active

def special_keys(key, x, y):
    global player_lane_index, steer_target_x
    if state == GAME:
        if key == GLUT_KEY_RIGHT:
            player_lane_index = max(0, player_lane_index - 1)
        elif key == GLUT_KEY_LEFT:
            player_lane_index = min(len(lanes) - 1, player_lane_index + 1)
        steer_target_x = lanes[player_lane_index]

def mouse_click(button, state, x, y):
    pass

# =====================================================================================
# SECTION 7: INITIALIZATION AND MAIN ENTRY POINT
# =====================================================================================

def init_opengl():
    glClearColor(0.2, 0.2, 0.3, 1)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"3D Racing Game - Final")
    
    init_opengl()
    
    glutDisplayFunc(draw_scene)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_click)
    
    glutMainLoop()

if __name__ == "__main__":
    main()