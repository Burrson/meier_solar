import pygame
import datetime
import ephem
import math
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

# Create a geocoder
geolocator = Nominatim(user_agent="solar_panel_positioning")

# Create a timezone finder
timezone_finder = TimezoneFinder()

# Prompt the user for a city or location
location_name = input("Enter a city or location: ")

# Use geocoding to obtain coordinates for the location
location = geolocator.geocode(location_name)

if location:
    latitude = location.latitude
    longitude = location.longitude

    # Initialize Pygame
    pygame.init()

    # Constants for Pygame display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    FONT_SIZE = 20

    # Create a Pygame window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Solar Panel Positioning")

    # Pygame font for displaying text
    font = pygame.font.Font(None, FONT_SIZE)

    # Function to draw the 3D solar panel
    def draw_solar_panel(pan_angle, tilt_angle):
        panel_length = 100
        panel_width = 100

        # Calculate the corner points of the 3D panel
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

        # Rotate the panel based on pan_angle (around its center)
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

        # Calculate the coordinates after tilting based on tilt_angle
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

        # Draw the 3D panel as a filled polygon
        pygame.draw.polygon(
            screen,
            BLACK,
            [top_left_tilted, top_right_tilted, bottom_right_tilted, bottom_left_tilted],
        )

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Create an observer for the specified location
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)

        # Determine the timezone for the location
        timezone_str = timezone_finder.timezone_at(lng=longitude, lat=latitude)

        if timezone_str:
            # Use the determined timezone
            local_timezone = pytz.timezone(timezone_str)

            # Get the current time in the local timezone
            current_time = datetime.datetime.now(local_timezone)
        else:
            # Fallback to UTC if timezone cannot be determined
            local_timezone = pytz.utc
            current_time = datetime.datetime.now(pytz.utc)

        # Set the observer's date and time
        observer.date = current_time

        sun = ephem.Sun(observer)

        # alt — Altitude ±90° relative to the horizon’s great circle (unaffected by the rise/set setting horizon)
        solar_altitude = math.degrees(sun.alt)

        # az — Azimuth 0°–360° east of north
        solar_azimuth = math.degrees(sun.az)

        optimal_pan_angle = solar_azimuth

        optimal_tilt_angle = 90 - solar_altitude

        # Clear the screen
        screen.fill(WHITE)

        # Draw the 3D solar panel
        draw_solar_panel(optimal_pan_angle, optimal_tilt_angle)

        # Print the results on the screen
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

        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
else:
    print("Location not found.")
