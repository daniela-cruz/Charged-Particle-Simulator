#ifndef ENGINE_H
#define ENGINE_H

#include <math.h>

typedef struct {
    double x, y, vx, vy, radius;
    double mass;
    double charge;
} Particle;

// הצהרה על הפונקציה (Function Prototype)
void update_positions(Particle* particles, int n, double dt, double width, double height, 
                      double gravity, double mag_field, double elec_field_x, double elec_field_y);

#endif