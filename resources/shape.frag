#version 430

out vec4 fragColor;

uniform sampler2D u_texture;
// uniform sampler2DMS msaa_texture;

void main() {
    ivec2 uv = ivec2(gl_FragCoord.xy);
    vec3 texel_color = texelFetch(u_texture, uv, 0).rgb;

    vec3 color = vec3(1.0, 1.0, 1.0);

    if (texel_color.r > 0.5) {
        color = vec3(0.0, 0.0, 0.0);
    }

    fragColor = vec4(color, 1.0);
}
