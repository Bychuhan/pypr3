#version 330 core

in vec2 in_pos;
in vec2 in_texCoord;

out vec2 v_texCoord;

uniform vec2 u_position;
uniform vec2 u_textureSize;
uniform vec2 u_anchor;
uniform float u_rotation;
uniform vec2 u_scale;

uniform vec2 u_screenSize;

void main() {
    vec2 anchorOffset = (-(u_anchor - 0.5)) * u_textureSize * 2.;

    float c = cos(radians(u_rotation));
    float s = sin(radians(u_rotation));
    mat2 rotMat = mat2(c, -s, s, c);

    vec2 ndcPos = ((u_textureSize * in_pos + anchorOffset) * u_scale * rotMat + u_position * 2.) / u_screenSize;

    gl_Position = vec4(ndcPos, 0., 1.);

    v_texCoord = in_texCoord;
}
