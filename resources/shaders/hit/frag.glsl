#version 330 core

in vec4 v_color;
in vec2 v_texCoord;
flat in int v_frameIndex;

out vec4 fragColor;

uniform sampler2D u_hitTexture;
uniform vec2 u_gridSize;

void main() {
    float cols = u_gridSize.x;
    float rows = u_gridSize.y;

    float frameWidth = 1.0 / cols;
    float frameHeight = 1.0 / rows;

    float col = mod(v_frameIndex, cols);
    float row = floor(v_frameIndex / cols);

    row = rows - 1.0 - row;

    vec2 offset = vec2(col * frameWidth, row * frameHeight);
    vec2 uv = v_texCoord * vec2(frameWidth, frameHeight) + offset;

    fragColor = texture(u_hitTexture, uv) * v_color;
}
