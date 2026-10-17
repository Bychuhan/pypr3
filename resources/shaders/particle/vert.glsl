#version 330 core

in vec2 in_pos;
in vec2 in_center;
in float in_size;
in vec4 in_color;

out vec4 v_color;

uniform vec2 u_screenSize;

void main() {
    vec2 ndcPos = (in_center * 2. + vec2(in_size) * in_pos) / u_screenSize;

    gl_Position = vec4(ndcPos, 0., 1.);

    v_color = in_color;
}
