#include "engine.h"

void update_positions(Particle* particles, int n, double dt, double width, double height, 
                      double gravity, double mag_field, double elec_field_x, double elec_field_y) {
    
    // --- 1. עדכון מיקומים ותאוצות (Euler Integration) ---
    for (int i = 0; i < n; i++) {
        // חישוב כוחות (חשמלי + מגנטי + כבידה)
        double ax = (particles[i].charge * (elec_field_x + mag_field * particles[i].vy)) / particles[i].mass;
        double ay = gravity + (particles[i].charge * (elec_field_y - mag_field * particles[i].vx)) / particles[i].mass;

        particles[i].vx += ax * dt;
        particles[i].vy += ay * dt;
        particles[i].x += particles[i].vx * dt;
        particles[i].y += particles[i].vy * dt;
    }

    // --- 2. טיפול בהתנגשויות בין חלקיקים (Elastic Collision) ---
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            double dx = particles[j].x - particles[i].x;
            double dy = particles[j].y - particles[i].y;
            double distance_sq = dx * dx + dy * dy;
            double min_dist = particles[i].radius + particles[j].radius;

            if (distance_sq < min_dist * min_dist) {
                double dist = sqrt(distance_sq);
                if (dist == 0) continue; // מניעת חלוקה באפס במקרה קצה

                // תיקון חפיפה (Static Resolution)
                double overlap = 0.5 * (min_dist - dist);
                particles[i].x -= overlap * (dx / dist);
                particles[i].y -= overlap * (dy / dist);
                particles[j].x += overlap * (dx / dist);
                particles[j].y += overlap * (dy / dist);

                // עדכון מהירויות (Dynamic Resolution)
                double dvx = particles[i].vx - particles[j].vx;
                double dvy = particles[i].vy - particles[j].vy;
                double dot_product = dvx * dx + dvy * dy;
                
                if (dot_product < 0) { // מתנגשים רק אם הם נעים אחד כלפי השני
                    double common_factor = (2.0 * dot_product) / (distance_sq * (particles[i].mass + particles[j].mass));
                    particles[i].vx -= common_factor * particles[j].mass * dx;
                    particles[i].vy -= common_factor * particles[j].mass * dy;
                    particles[j].vx += common_factor * particles[i].mass * dx;
                    particles[j].vy += common_factor * particles[i].mass * dy;
                }
            }
        }
    }

    // --- 3. טיפול סופי בקירות (Boundary Conditions) ---
    // אנחנו עושים את זה בסוף כדי לוודא שאף חלקיק לא נדחף החוצה מהתנגשות
    for (int i = 0; i < n; i++) {
        // רצפה
        if (particles[i].y < particles[i].radius) {
            particles[i].y = particles[i].radius;
            particles[i].vy *= -0.5; // איבוד אנרגיה
            particles[i].vx *= 0.95; // חיכוך
        }
        // תקרה
        else if (particles[i].y > height - particles[i].radius) {
            particles[i].y = height - particles[i].radius;
            particles[i].vy *= -0.8;
        }

        // קיר שמאלי
        if (particles[i].x < particles[i].radius) {
            particles[i].x = particles[i].radius;
            particles[i].vx *= -0.8;
        }
        // קיר ימני
        else if (particles[i].x > width - particles[i].radius) {
            particles[i].x = width - particles[i].radius;
            particles[i].vx *= -0.8;
        }
    }
}