#version 330 core
out vec3 f_color;

in vec2 uv;

uniform sampler2D tex;

void main()
{
    vec4 col = texture(tex, uv);
    if (col.a < 0.5)
    {
        discard;
        return;
    }
    f_color = col.rgb;
}