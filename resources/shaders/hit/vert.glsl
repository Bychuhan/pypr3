#version 330 core

in vec2 in_pos;
in vec2 in_texCoord;
in vec2 position;
in vec4 in_color;
in float in_frame;

out vec2 texCoord;
out vec4 color;
flat out int frameIndex;

uniform vec2 textureSize;
uniform vec2 screenSize;

void main() {
    vec2 realPos = (position * 2 + textureSize * in_pos) / screenSize;

    gl_Position = vec4(realPos, 0., 1.);

    texCoord = in_texCoord;
    color = in_color;
    frameIndex = int(in_frame);
}