#version 330 core

in vec2 in_pos;

uniform vec2 u_position;
uniform vec2 u_size;
uniform vec2 u_anchor;
uniform float u_rotation;

uniform vec2 u_screenSize;

void main() {
    vec2 anchorOffset = (-(u_anchor - 0.5)) * u_size * 2.;

    float c = cos(radians(u_rotation));
    float s = sin(radians(u_rotation));
    mat2 rotMat = mat2(c, -s, s, c);

    vec2 ndcPos = ((u_size * in_pos + anchorOffset) * rotMat + u_position * 2.) / u_screenSize;

    gl_Position = vec4(ndcPos, 0., 1.);
}
