#version 330 core
in vec3 FragPos;
in vec3 Normal; // 法向量
uniform vec3 lightPos; // 光源位置
uniform vec3 viewPos; // 观察者位置
uniform vec3 lightColor; // 光源颜色
uniform vec3 objectColor; // 物体颜色

uniform float ambientStrength = 0.1; // 环境光强度
uniform float specularStrength = 0.4; // 镜面光强度
uniform int shininess = 16; // 镜面光高光大小

out vec4 FragColor;

// FXAA抗锯齿函数
vec3 applyFXAA(sampler2D tex, vec2 fragCoord, vec2 resolution, float reduceMul, float reduceMin) {
    vec3 rgbNW = texture(tex, (fragCoord + vec2(-1.0, -1.0)) / resolution).xyz;
    vec3 rgbNE = texture(tex, (fragCoord + vec2(1.0, -1.0)) / resolution).xyz;
    vec3 rgbSW = texture(tex, (fragCoord + vec2(-1.0, 1.0)) / resolution).xyz;
    vec3 rgbSE = texture(tex, (fragCoord + vec2(1.0, 1.0)) / resolution).xyz;
    vec4 rgbaM = texture(tex, fragCoord / resolution);
    vec3 rgbM = rgbaM.xyz;
    float opacity = rgbaM.w;
    vec3 luma = vec3(0.299, 0.587, 0.114);
    float lumaNW = dot(rgbNW, luma);
    float lumaNE = dot(rgbNE, luma);
    float lumaSW = dot(rgbSW, luma);
    float lumaSE = dot(rgbSE, luma);
    float lumaM = dot(rgbM, luma);
    float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
    float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

    vec2 dir;
    dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
    dir.y = ((lumaNW + lumaSW) - (lumaNE + lumaSE));

    float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * reduceMul), reduceMin);

    float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);
    dir = min(vec2(reduceMul, reduceMul), max(vec2(-reduceMul, -reduceMul), dir * rcpDirMin)) * resolution;

    vec3 rgbA = 0.5 * (
        texture(tex, fragCoord / resolution + dir / resolution).xyz +
        texture(tex, fragCoord / resolution + dir.xy / resolution).xyz
    );
    vec3 rgbB = rgbA * 0.5 + 0.25 * (
        texture(tex, fragCoord / resolution + dir * 2.0 / resolution).xyz +
        texture(tex, fragCoord / resolution + dir.xy * 2.0 / resolution).xyz
    );
    float lumaB = dot(rgbB, luma);
    if ((lumaB < lumaMin) || (lumaB > lumaMax)) {
        FragColor = vec4(rgbA, opacity);
    } else {
        FragColor = vec4(rgbB, opacity);
    }
    return FragColor.rgb;
}

void main() {
    // 计算光线方向和法向量之间的角度
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(Normal, lightDir), 0.0);

    // 计算角度的权重
    float angleWeight = (diff + 1.0) / 2.0; // 角度值范围从[-1,1]映射到[0,1]

    // 使用角度权重来混合颜色
    vec3 diffuse = mix(lightColor * objectColor, objectColor, angleWeight);

    // 环境光照计算
    vec3 ambient = ambientStrength * lightColor;

    // 镜面光照计算
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = specularStrength * spec * lightColor;

    // 最终颜色
    vec3 result = (ambient + diffuse + specular);
    FragColor = vec4(result, 1.0);
}
