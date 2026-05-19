#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>
#include "frames.h"

// Use page buffer mode on Uno to save SRAM
U8G2_SH1106_128X64_NONAME_1_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
// Table of pointers to each frame array, also stored in flash

const uint8_t* const animationFrames[3] PROGMEM = {
  frame_000,
  frame_001,
  frame_002
};



void drawFrame(uint8_t index) {
  // Read pointer to the selected frame from PROGMEM
  const uint8_t* framePtr = (const uint8_t*)pgm_read_ptr(&animationFrames[index]);

  u8g2.firstPage();
  do {
    u8g2.drawXBMP(0, 0, 64, 64, framePtr);
  } while (u8g2.nextPage());
}

void setup() {
  u8g2.begin();
}

void loop() {
  static uint8_t currentFrame = 0;

  drawFrame(currentFrame);
  delay(100);

  currentFrame++;
  if (currentFrame >= 3) {
    currentFrame = 0;
  }
}
