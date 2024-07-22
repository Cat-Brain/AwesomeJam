#version 330 core
out vec3 f_color;

in vec2 uv;

uniform sampler2D tex;

void main()
{
    f_color = texture(tex, uv).rgb;
}