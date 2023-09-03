import pygame
import datetime
import ephem
import math
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

solarImage = pygame.image.load("image.jpg")
geolocator = Nominatim(user_agent="solar_panel_positioning")
timezone_finder = TimezoneFinder()

location_name = input("Enter a city or location: ")

location = geolocator.geocode(location_name)

if location:
    latitude = location.latitude
    longitude = location.longitude

    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    FONT_SIZE = 20
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 40
    BUTTON_MARGIN = 10
    BUTTON_COLOR = (0, 128, 255)
    BUTTON_TEXT_COLOR = (255, 255, 255)

    current_mode = 'dual'
    current_mode_text = 'Dual Axis Mode'  # Initialize with dual-axis mode

    def lerp( p1, p2, f ):
        return p1 + f * (p2 - p1)

    def lerp2d( p1, p2, f ):
        return tuple( lerp( p1[i], p2[i], f ) for i in range(2) )

    def draw_quad( surface, quad, img ):

        points = dict()

        for i in range( img.get_size()[1]+1 ):
            b = lerp2d( quad[1], quad[2], i/img.get_size()[1] )
            c = lerp2d( quad[0], quad[3], i/img.get_size()[1] )
            for u in range( img.get_size()[0]+1 ):
                a = lerp2d( c, b, u/img.get_size()[0] )
                points[ (u,i) ] = a

        for x in range( img.get_size()[0] ):
            for y in range( img.get_size()[1] ):
                pygame.draw.polygon(
                    surface,
                    img.get_at((x,y)),
                    [ points[ (a,b) ] for a, b in [ (x,y), (x,y+1), (x+1,y+1), (x+1,y) ] ] 
                )

    def switch_mode():
        global current_mode, current_mode_text
        if current_mode == 'dual':
            current_mode = 'single'
            current_mode_text = 'Single Axis Mode'
        else:
            current_mode = 'dual'
            current_mode_text = 'Dual Axis Mode'


    def draw_solar_panel(pan_angle, tilt_angle):
        panel_length = 100
        panel_width = 100

        top_left = [
            SCREEN_WIDTH // 2 - panel_length / 2,
            SCREEN_HEIGHT // 2 - panel_width / 2,
        ]
        top_right = [
            SCREEN_WIDTH // 2 + panel_length / 2,
            SCREEN_HEIGHT // 2 - panel_width / 2,
        ]
        bottom_left = [
            SCREEN_WIDTH // 2 - panel_length / 2,
            SCREEN_HEIGHT // 2 + panel_width / 2,
        ]
        bottom_right = [
            SCREEN_WIDTH // 2 + panel_length / 2,
            SCREEN_HEIGHT // 2 + panel_width / 2,
        ]

        center_x = (top_left[0] + top_right[0]) / 2
        center_y = (top_left[1] + bottom_left[1]) / 2
        angle_rad = math.radians(pan_angle)
        top_left_rot = [
            center_x
            + (top_left[0] - center_x) * math.cos(angle_rad)
            - (top_left[1] - center_y) * math.sin(angle_rad),
            center_y
            + (top_left[0] - center_x) * math.sin(angle_rad)
            + (top_left[1] - center_y) * math.cos(angle_rad),
        ]
        top_right_rot = [
            center_x
            + (top_right[0] - center_x) * math.cos(angle_rad)
            - (top_right[1] - center_y) * math.sin(angle_rad),
            center_y
            + (top_right[0] - center_x) * math.sin(angle_rad)
            + (top_right[1] - center_y) * math.cos(angle_rad),
        ]
        bottom_left_rot = [
            center_x
            + (bottom_left[0] - center_x) * math.cos(angle_rad)
            - (bottom_left[1] - center_y) * math.sin(angle_rad),
            center_y
            + (bottom_left[0] - center_x) * math.sin(angle_rad)
            + (bottom_left[1] - center_y) * math.cos(angle_rad),
        ]
        bottom_right_rot = [
            center_x
            + (bottom_right[0] - center_x) * math.cos(angle_rad)
            - (bottom_right[1] - center_y) * math.sin(angle_rad),
            center_y
            + (bottom_right[0] - center_x) * math.sin(angle_rad)
            + (bottom_right[1] - center_y) * math.cos(angle_rad),
        ]

        tilt_angle_rad = math.radians(tilt_angle)
        top_left_tilted = [
            top_left_rot[0],
            center_y
            + (top_left_rot[1] - center_y) * math.cos(tilt_angle_rad),
        ]
        top_right_tilted = [
            top_right_rot[0],
            center_y
            + (top_right_rot[1] - center_y) * math.cos(tilt_angle_rad),
        ]
        bottom_left_tilted = [
            bottom_left_rot[0],
            center_y
            + (bottom_left_rot[1] - center_y) * math.cos(tilt_angle_rad),
        ]
        bottom_right_tilted = [
            bottom_right_rot[0],
            center_y
            + (bottom_right_rot[1] - center_y) * math.cos(tilt_angle_rad),
        ]

        draw_quad(
            screen, 
            [top_left_tilted, top_right_tilted, bottom_right_tilted, bottom_left_tilted],
            solarImage,
        )

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Solar Panel Positioning")
    font = pygame.font.Font(None, FONT_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if BUTTON_RECT.collidepoint(event.pos):
                    switch_mode()

        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)

        timezone_str = timezone_finder.timezone_at(lng=longitude, lat=latitude)

        if timezone_str:
            local_timezone = pytz.timezone(timezone_str)
            current_time = datetime.datetime.now(local_timezone)
        else:
            local_timezone = pytz.utc
            current_time = datetime.datetime.now(pytz.utc)

        observer.date = current_time

        sun = ephem.Sun(observer)
        solar_altitude = math.degrees(sun.alt)
        solar_azimuth = math.degrees(sun.az)

        if current_mode == 'dual':
            optimal_pan_angle = solar_azimuth
            optimal_tilt_angle = 90 - solar_altitude
        else:
            # Single-axis mode (horizontal tracking)
            optimal_pan_angle = 180  # Keep the pan angle fixed (e.g., facing south)
            optimal_tilt_angle = solar_altitude  # Adjust the tilt angle based on solar altitude

        screen.fill(WHITE)
        draw_solar_panel(optimal_pan_angle, optimal_tilt_angle)

        location_text = font.render(f"Location: {location_name}", True, BLACK)
        time_text = font.render(
            f"Current Time (local timezone): {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
            True,
            BLACK,
        )
        altitude_text = font.render(
            f"Solar Altitude: {solar_altitude:.2f} degrees", True, BLACK
        )
        azimuth_text = font.render(
            f"Solar Azimuth: {solar_azimuth:.2f} degrees", True, BLACK
        )
        pan_angle_text = font.render(
            f"Optimal Pan Angle: {optimal_pan_angle:.2f} degrees", True, BLACK
        )
        tilt_angle_text = font.render(
            f"Optimal Tilt Angle: {optimal_tilt_angle:.2f} degrees", True, BLACK
        )

        screen.blit(location_text, (10, 10))
        screen.blit(time_text, (10, 30))
        screen.blit(altitude_text, (10, 50))
        screen.blit(azimuth_text, (10, 70))
        screen.blit(pan_angle_text, (10, 90))
        screen.blit(tilt_angle_text, (10, 110))

        BUTTON_RECT = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

        pygame.draw.rect(screen, BUTTON_COLOR, BUTTON_RECT)
        button_font = pygame.font.Font(None, 36)
        button_text = button_font.render(
            f'Switch to {current_mode.capitalize()} Axis', True, BUTTON_TEXT_COLOR
        )
        screen.blit(button_text, BUTTON_RECT.move(10, 5))

        # Add this code inside the main Pygame loop
        mode_text = font.render(f"Mode: {current_mode_text}", True, BLACK)
        screen.blit(mode_text, (10, 130))  # Adjust the position as needed

        pygame.display.flip()



    pygame.quit()
else:
    print("Location not found.")
