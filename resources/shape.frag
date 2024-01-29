#version 430 core

out vec4 f_color;

uniform sampler2D u_texture;

void main() {
    ivec2 uv = ivec2(gl_FragCoord.xy);
    vec3 texel_color = texelFetch(u_texture, uv, 0).rgb;

    vec3 color = vec3(1.0, 1.0, 1.0);

    if (texel_color.r > 0.5) {
        color = vec3(0.0, 0.0, 0.0);
    }

    f_color = vec4(color, 1.0);
}
