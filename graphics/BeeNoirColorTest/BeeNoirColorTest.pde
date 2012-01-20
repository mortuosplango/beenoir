int numColors = 9;

String[] hexColors = {
  "EDFF00",
  "FF0000",
  "2600FF",
  "006100",
  "6400A3",
  "FF7100",
  "B4B4B4",
  "FF00FF",
  "00FF3F"
};

color[] colors;

void setup() {
  colors = new color[numColors];
  
  // populate color table
  
  // out of hex colors
  /*
  for(int i = 0; i < numColors; i++) {
    colors[i] = unhex("FF" + hexColors[i]);
  }
  */
  
  // construct HSB colors
  colorMode(HSB, 255);
  for(int i = 0; i < numColors; i++) {
    int h = (int)(((float) i / (float) (numColors - 1)) * 255.0);
    int v = 192;
    if(i % 2 == 0) {
      v = v + 64; 
    }

    colors[i] = color(h, 255, v);
    
    if(i == 8) {
      colors[i] = color(255, 0, 192);
    }
  }
  
  size(800, 800);
}

void draw() {
 noStroke();
 background(0);
 
 for(int y = 0; y < numColors; y++) {
    for(int x = 0; x < numColors; x++) {
      int dim = (700/numColors);
      int sx = 50 + x * dim;
      int sy = 50 + y * dim;
      
      if(x == y) {
       /* fill(colors[x]);
       rect(sx, sy, dim, dim); */
      } else {
       fill(colors[x]);
       rect(sx + 5, sy + 5, dim/2, dim - 10);
      fill(colors[y]);
       rect(sx + dim/2, sy + 5, dim/2 - 5, dim - 10); 
      }
    }
 } 
}
