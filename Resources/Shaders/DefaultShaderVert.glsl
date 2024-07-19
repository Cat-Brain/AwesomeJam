#version 330 core
in vec2 aPos;
uniform mat4 camera;

void main()
{
    gl_Position = camera * vec4(aPos, .5, 1.0);
}