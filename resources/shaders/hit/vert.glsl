#version 330 core

in vec2 in_pos;
in vec2 in_texCoord;

out vec2 texCoord;

uniform vec2 position;
uniform vec2 textureSize;

uniform vec2 screenSize;

void main() {
    vec2 realPos = (position * 2 + textureSize * in_pos) / screenSize;

    gl_Position = vec4(realPos, 0., 1.);

    texCoord = in_texCoord;
}