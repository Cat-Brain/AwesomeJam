#version 330 core
in vec2 aPos, aUV;

out vec2 uv;

void main()
{
    gl_Position = vec4(aPos, .5, 1.0);
    uv = aUV;
}