#version 330 core

in vec2 texCoord;
in vec4 color;
flat in int frameIndex;

out vec4 fragColor;

uniform sampler2D texture;
uniform vec2 gridSize;

void main() {
    float cols = gridSize.x;
    float rows = gridSize.y;

    float frameWidth = 1.0 / cols;
    float frameHeight = 1.0 / rows;

    float col = mod(frameIndex, cols);
    float row = floor(frameIndex / cols);

    row = rows - 1.0 - row;

    vec2 offset = vec2(col * frameWidth, row * frameHeight);
    vec2 uv = texCoord * vec2(frameWidth, frameHeight) + offset;

    fragColor = texture2D(texture, uv) * color;
}