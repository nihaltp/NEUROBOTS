#include <Adafruit_NeoPixel.h>

// On most ESP32-S3 boards, including the S3-Mini-1, the built-in RGB LED is on GPIO 48.
#define RGB_PIN 48    
#define NUM_PIXELS 1  // Only one onboard RGB LED

Adafruit_NeoPixel pixels(NUM_PIXELS, RGB_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.setBrightness(255); // Set brightness (0-255)
}

void loop() {
  // Set the LED to Red
  pixels.setPixelColor(0, pixels.Color(255, 0, 0));
  pixels.show();
  delay(1000);
  
  // Set the LED to Green
  pixels.setPixelColor(0, pixels.Color(0, 255, 0));
  pixels.show();
  delay(1000);
  
  // Set the LED to Blue
  pixels.setPixelColor(0, pixels.Color(0, 0, 255));
  pixels.show();
  delay(1000);
}
