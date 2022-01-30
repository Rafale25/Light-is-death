#version 430

in vec2 v_vert;

uniform mat4 u_projectionMatrix;
uniform mat4 u_modelMatrix;
// uniform mat4 u_viewMatrix;

void main() {
    gl_Position = u_projectionMatrix * u_modelMatrix * vec4(v_vert, 0.0, 1.0);
}
