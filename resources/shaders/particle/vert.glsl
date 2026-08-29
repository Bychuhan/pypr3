#version 330 core

in vec2 in_pos;

uniform vec2 position;
uniform vec2 size;

uniform vec2 screenSize;

void main() {
    vec2 realPos = (position * 2 + size * in_pos) / screenSize;

    gl_Position = vec4(realPos, 0., 1.);
}
