//PiDRO 
//by Alan Campbell
//July 2014

/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
*/
int CAL_CLK = 2; //Caliper Clock Pin wire to 2
int CAL_DATA = 8; //Caliper Data Pin

int flag = 0;
boolean databits[21];
int clocktimes[21];
int curdatabit = 0;
int Ndatabits = 20;
int i;
int data;
long value = 0;

void setup() {
  for (i = 0; i < Ndatabits; i++) {     
    databits[i] = 0;
  } 
  Serial.begin(19200); 
  pinMode(CAL_CLK, INPUT);  // Clock pin = 2
  pinMode(CAL_DATA, INPUT); // Data pin = 8 
  attachInterrupt(0, dataReceived,FALLING); // RISING FALLING
}

void dataReceived() { // do not put a lot of calcs here - keep fast so it finishes 
  if ( curdatabit < Ndatabits ) {
    databits[curdatabit] = digitalRead(CAL_DATA); // read DATA value as soon as possible 
    curdatabit = curdatabit + 1;    
  } else {
    flag = 1;
  }
}

void loop() {
 if(flag) {   
       for (i = 3; i < Ndatabits; i++) {  // skip first 3 bits
         if( databits[i] == 1 ){  // correct for transistor bit flip 
           databits[i] = 0;
           bitClear( value, i-3 );
         }else{
           databits[i] = 1; 
           bitSet( value, i-3 );
         } 
         Serial.print(databits[i]);
       }
       Serial.print("  "); 
       if ( value > 20000 )  { // tests for a negative scale readings
         for ( i=16; i<32; i++ ) {  // set the bits for negative
           bitSet( value, i );
         }   
       }   
       value = .99219 * value + 653;  // each caliper is different
       Serial.println( value, DEC );    
   
       for (i = 0; i < Ndatabits; i++) {     
        databits[i] = 0;
       } 
       curdatabit = 0;
       value = 0;
       flag = 0;     
 }
}


