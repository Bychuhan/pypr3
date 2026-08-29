#version 330 core

in vec2 in_pos;
in vec2 position;
in float size;
in vec4 in_color;

out vec4 color;

uniform vec2 screenSize;

void main() {
    vec2 realPos = (position * 2 + vec2(size) * in_pos) / screenSize;

    gl_Position = vec4(realPos, 0., 1.);

    color = in_color;
}
