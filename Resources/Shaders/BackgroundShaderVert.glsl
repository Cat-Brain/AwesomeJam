#version 330 core
in vec2 aPos, aUV;
uniform mat4 camera;

out vec2 pos, uv;

void main()
{
    gl_Position = vec4(aPos, .5, 1.0);
    uv = aUV;
    pos = vec2(camera * vec4(aPos, .5, 1.0));
}