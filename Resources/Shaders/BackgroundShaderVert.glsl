#version 330 core
in vec2 aPos, aUV;

uniform vec4 minMaxPos;

out vec2 pos;

void main()
{
    gl_Position = vec4(aPos, .5, 1.0);
    pos = minMaxPos.xy * (1 - aUV) + minMaxPos.zw * aUV;
}