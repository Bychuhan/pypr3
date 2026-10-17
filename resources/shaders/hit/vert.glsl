#version 330 core

in vec2 in_pos;
in vec2 in_texCoord;
in vec2 in_center;
in vec4 in_color;
in float in_frameIndex;

out vec2 v_texCoord;
out vec4 v_color;
flat out int v_frameIndex;

uniform vec2 u_hitTextureSize;
uniform vec2 u_screenSize;

void main() {
    vec2 ndcPos = (in_center * 2. + u_hitTextureSize * in_pos) / u_screenSize;

    gl_Position = vec4(ndcPos, 0., 1.);

    v_texCoord = in_texCoord;
    v_color = in_color;
    v_frameIndex = int(in_frameIndex);
}
