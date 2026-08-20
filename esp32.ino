#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

// --- Wi-Fi & Server Configuration ---
const char* ssid          = "Galaxy A14 5G A018";
const char* password      = "abc123def";
const char* serverAddress = "http://172.18.225.17:8000/api/analyze"; // Server IP receiving values

// --- Pin Assignments ---
#define ONE_WIRE_BUS 15     // Moved DS18B20 to GPIO 15 to free I2C pins
#define I2C_SDA      13     // ADS1115 SDA Pin
#define I2C_SCL      14     // ADS1115 SCL Pin

// ESP32-CAM AI-THINKER Camera Pin Definition
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// --- Deep Sleep Timing ---
#define TIME_TO_SLEEP 15                         // Sleep time in minutes
#define uS_TO_S_FACTOR 1000000ULL                // Microseconds to seconds conversion factor

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);
Adafruit_ADS1115 ads;

void setup() {
  Serial.begin(115200);
  delay(500);

  // 1. Initialize Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  int timeout = 0;
  while (WiFi.status() != WL_CONNECTED && timeout < 20) {
    delay(500);
    Serial.print(".");
    timeout++;
  }
  Serial.println("\nWi-Fi Connected!");

  // 2. Initialize DS18B20 Temp Sensor
  tempSensor.begin();
  tempSensor.requestTemperatures();
  float tempC = tempSensor.getTempCByIndex(0);

  // 3. Initialize I2C and ADS1115 for Turbidity Sensor
  Wire.begin(I2C_SDA, I2C_SCL);
  float turbidityVoltage = 0.0;
  
  if (ads.begin(0x48)) {
    ads.setGain(GAIN_ONE); // +/- 4.096V range
    
    // Average 10 readings from Channel A0 of the ADS1115
    int32_t adcSum = 0;
    for (int i = 0; i < 10; i++) {
      adcSum += ads.readADC_SingleEnded(0);
      delay(10);
    }
    int16_t adcAvg = adcSum / 10;
    turbidityVoltage = ads.computeVolts(adcAvg);
  } else {
    Serial.println("ADS1115 initialization failed!");
  }

  // 4. Initialize Camera Configuration
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_siod = SIOD_GPIO_NUM;
  config.pin_sioc = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed!");
    goToSleep();
  }

  // 5. Capture Image Frame
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed!");
    goToSleep();
  }

  // 6. Send HTTP POST Request with Data + Photo
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverAddress);

    String boundary = "----ESP32CAMBoundary";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

    String head = "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"temperature\"\r\n\r\n" + String(tempC) + "\r\n";
    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"turbidity\"\r\n\r\n" + String(turbidityVoltage) + "\r\n";
    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"image\"; filename=\"frame.jpg\"\r\n";
    head += "Content-Type: image/jpeg\r\n\r\n";

    String tail = "\r\n--" + boundary + "--\r\n";

    uint32_t totalLen = head.length() + fb->len + tail.length();
    
    uint8_t *buffer = (uint8_t *)malloc(totalLen);
    if (buffer) {
      memcpy(buffer, head.c_str(), head.length());
      memcpy(buffer + head.length(), fb->buf, fb->len);
      memcpy(buffer + head.length() + fb->len, tail.c_str(), tail.length());

      int httpResponseCode = http.POST(buffer, totalLen);
      Serial.print("HTTP Response Code: ");
      Serial.println(httpResponseCode);

      free(buffer);
    }
    http.end();
  }

  esp_camera_fb_return(fb);

  // 7. Enter Deep Sleep
  goToSleep();
}

void loop() {
  
}

void goToSleep() {
  Serial.println("Entering Deep Sleep for 15 minutes...");
  esp_sleep_enable_timer_wakeup((uint64_t)TIME_TO_SLEEP * 60 * uS_TO_S_FACTOR);
  esp_deep_sleep_start();
}