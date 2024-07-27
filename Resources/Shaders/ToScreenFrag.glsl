#version 330 core
out vec3 f_color;

in vec2 uv;

uniform sampler2D tex;
uniform vec2 stretch;

void main()
{
    f_color = texture(tex, stretch * uv).rgb;
}