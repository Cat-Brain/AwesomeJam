#version 330 core
in vec2 aPos;
uniform vec4 posScale;
uniform mat4 camera;

void main()
{
    gl_Position = camera * vec4(aPos * posScale.zw + posScale.xy, .5, 1.0);
}