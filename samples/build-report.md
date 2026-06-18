# Dependency Report

Checked **61** dependencies across enabled data sources.

## Summary

Severity is the highest-impact finding for a dependency across all enabled sources: OSV vulnerabilities, endoflife.date lifecycle status, and deps.dev version-currency signals. `unknown` means the tool found a relevant issue but could not rank it confidently; `none` means no problem was found.

| Top severity | Count |
| --- | --- |
| High | 2 |
| Medium | 14 |
| Low | 19 |
| Unknown | 2 |
| None | 24 |

## Results

| File | Ecosystem | Package | Current version | Latest version | EOL | Vulns | Severity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eol-checker/samples/build.gradle:55 | maven | org.json:json | 20250107 | 20260522 | unmapped | 0 | High |
| eol-checker/samples/build.gradle:72 | maven | org.springframework.boot:spring-boot-starter-actuator | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 2 (CVE-2026-22731, CVE-2026-22733) | High |
| eol-checker/samples/build.gradle:6 | maven | org.springframework.boot:org.springframework.boot.gradle.plugin | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:41 | maven | org.springframework.boot:spring-boot-starter-web | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:42 | maven | org.springframework.boot:spring-boot-starter-oauth2-resource-server | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:43 | maven | org.springframework.boot:spring-boot-starter-security | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:44 | maven | org.springframework.boot:spring-boot-starter-oauth2-client | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:45 | maven | org.springframework.boot:spring-boot-starter-webflux | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:46 | maven | org.springframework.boot:spring-boot-starter-data-mongodb | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:47 | maven | org.springframework.ai:spring-ai-bom | 1.1.2 | 2.0.0 | unmapped | 0 | Medium |
| eol-checker/samples/build.gradle:59 | maven | org.springdoc:springdoc-openapi-bom | 2.8.15 | 3.0.3 | unmapped | 0 | Medium |
| eol-checker/samples/build.gradle:65 | maven | org.springframework.boot:spring-boot-configuration-processor | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:91 | maven | org.springframework.boot:spring-boot-starter-test | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:93 | maven | org.springframework.boot:spring-boot-test-autoconfigure | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:94 | maven | org.springframework.cloud:spring-cloud-contract-wiremock | 4.1.4 | 5.0.3 | unmapped | 0 | Medium |
| eol-checker/samples/build.gradle:95 | maven | org.springframework.boot:spring-boot-testcontainers | 3.5.10 | 4.1.0 | supported (EOL: 2026-06-30) | 0 | Medium |
| eol-checker/samples/build.gradle:4 | maven | com.diffplug.spotless:com.diffplug.spotless.gradle.plugin | 8.6.0 | 8.7.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:5 | maven | org.sonarqube:org.sonarqube.gradle.plugin | 7.3.0.8198 | 7.3.1.8318 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:35 | maven | io.opentelemetry:opentelemetry-bom | 1.44.1 | 1.63.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:36 | maven | io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom | 2.24.0 | 2.28.1 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:52 | maven | net.sourceforge.tess4j:tess4j | 5.13.0 | 5.19.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:53 | maven | org.apache.pdfbox:pdfbox | 3.0.6 | 3.0.7 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:56 | maven | org.bytedeco:javacv-platform | 1.5.12 | 1.5.13 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:57 | maven | commons-codec:commons-codec | 1.21.0 | 1.22.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:67 | maven | org.mapstruct:mapstruct | 1.6.3 | 1.7.0.Beta1 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:68 | maven | org.mapstruct:mapstruct-processor | 1.6.3 | 1.7.0.Beta1 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:74 | maven | com.microsoft.azure:applicationinsights-web | 3.7.2 | 3.7.8 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:75 | maven | com.microsoft.azure:applicationinsights-runtime-attach | 3.7.2 | 3.7.8 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:77 | maven | io.github.resilience4j:resilience4j-spring-boot3 | 2.3.0 | 2.4.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:80 | maven | io.opentelemetry:opentelemetry-bom | 1.44.1 | 1.63.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:81 | maven | io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom | 2.24.0 | 2.28.1 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:85 | maven | io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter | 2.24.0 | 2.28.1 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:96 | maven | org.testcontainers:testcontainers-bom | 2.0.3 | 2.0.5 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:99 | maven | net.datafaker:datafaker | 2.5.3 | 2.6.0 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:100 | maven | com.tngtech.archunit:archunit-junit5 | 1.4.1 | 1.4.2 | unmapped | 0 | Low |
| eol-checker/samples/build.gradle:73 | maven | com.configcat:configcat-java-client | 9.+ | 10.0.1 | unmapped | 0 | Unknown |
| eol-checker/samples/build.gradle:76 | maven | org.springframework.boot:spring-boot-starter-aop | 3.5.10 | 4.0.0-M2 | supported (EOL: 2026-06-30) | 0 | Unknown |
| eol-checker/samples/build.gradle:2 | maven | java:java.gradle.plugin | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:3 | maven | jacoco:jacoco.gradle.plugin | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:7 | maven | io.spring.dependency-management:io.spring.dependency-management.gradle.plugin | 1.1.7 | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:48 | maven | org.springframework.ai:spring-ai-starter-model-azure-openai | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:49 | maven | org.springframework.ai:spring-ai-starter-vector-store-mongodb-atlas | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:50 | maven | org.springframework.ai:spring-ai-advisors-vector-store | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:51 | maven | org.springframework.ai:spring-ai-pdf-document-reader | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:54 | maven | com.github.jai-imageio:jai-imageio-jpeg2000 | 1.4.0 | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:58 | maven | com.fasterxml.jackson.datatype:jackson-datatype-jdk8 | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:60 | maven | org.springdoc:springdoc-openapi-starter-webmvc-ui | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:63 | maven | org.projectlombok:lombok | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:66 | maven | org.projectlombok:lombok | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:69 | maven | org.projectlombok:lombok-mapstruct-binding | 0.2.0 | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:82 | maven | io.opentelemetry:opentelemetry-api | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:83 | maven | io.opentelemetry:opentelemetry-sdk | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:84 | maven | io.opentelemetry:opentelemetry-exporter-otlp | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:86 | maven | io.micrometer:micrometer-registry-otlp | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:88 | maven | io.micrometer:micrometer-tracing-bridge-otel | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:92 | maven | org.springframework.security:spring-security-test | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:97 | maven | org.testcontainers:testcontainers-junit-jupiter | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:98 | maven | org.testcontainers:testcontainers-mongodb | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:101 | maven | org.junit.platform:junit-platform-launcher | - | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:104 | maven | org.apache.commons:commons-collections4 | 4.5.0 | - | unmapped | 0 | None |
| eol-checker/samples/build.gradle:105 | maven | org.apache.commons:commons-lang3 | 3.20.0 | - | unmapped | 0 | None |

## Findings

### `org.json:json`

- Location: `eol-checker/samples/build.gradle:55`
- `deps.dev` / High: org.json:json is behind latest 20260522 - https://deps.dev/maven/org.json%3Ajson

### `org.springframework.boot:spring-boot-starter-actuator`

- Location: `eol-checker/samples/build.gradle:72`
- `osv` / High: Spring Boot has an Authentication Bypass under Actuator Health groups paths (`CVE-2026-22731`); fixed in `3.5.12` - https://osv.dev/vulnerability/GHSA-8hfc-fq58-r658
- `osv` / High: Spring Boot has an Authentication Bypass under Actuator CloudFoundry endpoints (`CVE-2026-22733`); fixed in `4.0.4` - https://osv.dev/vulnerability/GHSA-mgvc-8q2h-5pgc
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-actuator is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-actuator

### `org.springframework.boot:org.springframework.boot.gradle.plugin`

- Location: `eol-checker/samples/build.gradle:6`
- `deps.dev` / Medium: org.springframework.boot:org.springframework.boot.gradle.plugin is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aorg.springframework.boot.gradle.plugin

### `org.springframework.boot:spring-boot-starter-web`

- Location: `eol-checker/samples/build.gradle:41`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-web is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-web

### `org.springframework.boot:spring-boot-starter-oauth2-resource-server`

- Location: `eol-checker/samples/build.gradle:42`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-oauth2-resource-server is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-oauth2-resource-server

### `org.springframework.boot:spring-boot-starter-security`

- Location: `eol-checker/samples/build.gradle:43`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-security is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-security

### `org.springframework.boot:spring-boot-starter-oauth2-client`

- Location: `eol-checker/samples/build.gradle:44`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-oauth2-client is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-oauth2-client

### `org.springframework.boot:spring-boot-starter-webflux`

- Location: `eol-checker/samples/build.gradle:45`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-webflux is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-webflux

### `org.springframework.boot:spring-boot-starter-data-mongodb`

- Location: `eol-checker/samples/build.gradle:46`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-data-mongodb is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-data-mongodb

### `org.springframework.ai:spring-ai-bom`

- Location: `eol-checker/samples/build.gradle:47`
- `deps.dev` / Medium: org.springframework.ai:spring-ai-bom is behind latest 2.0.0 - https://deps.dev/maven/org.springframework.ai%3Aspring-ai-bom

### `org.springdoc:springdoc-openapi-bom`

- Location: `eol-checker/samples/build.gradle:59`
- `deps.dev` / Medium: org.springdoc:springdoc-openapi-bom is behind latest 3.0.3 - https://deps.dev/maven/org.springdoc%3Aspringdoc-openapi-bom

### `org.springframework.boot:spring-boot-configuration-processor`

- Location: `eol-checker/samples/build.gradle:65`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-configuration-processor is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-configuration-processor

### `org.springframework.boot:spring-boot-starter-test`

- Location: `eol-checker/samples/build.gradle:91`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-starter-test is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-test

### `org.springframework.boot:spring-boot-test-autoconfigure`

- Location: `eol-checker/samples/build.gradle:93`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-test-autoconfigure is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-test-autoconfigure

### `org.springframework.cloud:spring-cloud-contract-wiremock`

- Location: `eol-checker/samples/build.gradle:94`
- `deps.dev` / Medium: org.springframework.cloud:spring-cloud-contract-wiremock is behind latest 5.0.3 - https://deps.dev/maven/org.springframework.cloud%3Aspring-cloud-contract-wiremock

### `org.springframework.boot:spring-boot-testcontainers`

- Location: `eol-checker/samples/build.gradle:95`
- `deps.dev` / Medium: org.springframework.boot:spring-boot-testcontainers is behind latest 4.1.0 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-testcontainers

### `com.diffplug.spotless:com.diffplug.spotless.gradle.plugin`

- Location: `eol-checker/samples/build.gradle:4`
- `deps.dev` / Low: com.diffplug.spotless:com.diffplug.spotless.gradle.plugin is behind latest 8.7.0 - https://deps.dev/maven/com.diffplug.spotless%3Acom.diffplug.spotless.gradle.plugin

### `org.sonarqube:org.sonarqube.gradle.plugin`

- Location: `eol-checker/samples/build.gradle:5`
- `deps.dev` / Low: org.sonarqube:org.sonarqube.gradle.plugin is behind latest 7.3.1.8318 - https://deps.dev/maven/org.sonarqube%3Aorg.sonarqube.gradle.plugin

### `io.opentelemetry:opentelemetry-bom`

- Location: `eol-checker/samples/build.gradle:35`
- `deps.dev` / Low: io.opentelemetry:opentelemetry-bom is behind latest 1.63.0 - https://deps.dev/maven/io.opentelemetry%3Aopentelemetry-bom

### `io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom`

- Location: `eol-checker/samples/build.gradle:36`
- `deps.dev` / Low: io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom is behind latest 2.28.1 - https://deps.dev/maven/io.opentelemetry.instrumentation%3Aopentelemetry-instrumentation-bom

### `net.sourceforge.tess4j:tess4j`

- Location: `eol-checker/samples/build.gradle:52`
- `deps.dev` / Low: net.sourceforge.tess4j:tess4j is behind latest 5.19.0 - https://deps.dev/maven/net.sourceforge.tess4j%3Atess4j

### `org.apache.pdfbox:pdfbox`

- Location: `eol-checker/samples/build.gradle:53`
- `deps.dev` / Low: org.apache.pdfbox:pdfbox is behind latest 3.0.7 - https://deps.dev/maven/org.apache.pdfbox%3Apdfbox

### `org.bytedeco:javacv-platform`

- Location: `eol-checker/samples/build.gradle:56`
- `deps.dev` / Low: org.bytedeco:javacv-platform is behind latest 1.5.13 - https://deps.dev/maven/org.bytedeco%3Ajavacv-platform

### `commons-codec:commons-codec`

- Location: `eol-checker/samples/build.gradle:57`
- `deps.dev` / Low: commons-codec:commons-codec is behind latest 1.22.0 - https://deps.dev/maven/commons-codec%3Acommons-codec

### `org.mapstruct:mapstruct`

- Location: `eol-checker/samples/build.gradle:67`
- `deps.dev` / Low: org.mapstruct:mapstruct is behind latest 1.7.0.Beta1 - https://deps.dev/maven/org.mapstruct%3Amapstruct

### `org.mapstruct:mapstruct-processor`

- Location: `eol-checker/samples/build.gradle:68`
- `deps.dev` / Low: org.mapstruct:mapstruct-processor is behind latest 1.7.0.Beta1 - https://deps.dev/maven/org.mapstruct%3Amapstruct-processor

### `com.microsoft.azure:applicationinsights-web`

- Location: `eol-checker/samples/build.gradle:74`
- `deps.dev` / Low: com.microsoft.azure:applicationinsights-web is behind latest 3.7.8 - https://deps.dev/maven/com.microsoft.azure%3Aapplicationinsights-web

### `com.microsoft.azure:applicationinsights-runtime-attach`

- Location: `eol-checker/samples/build.gradle:75`
- `deps.dev` / Low: com.microsoft.azure:applicationinsights-runtime-attach is behind latest 3.7.8 - https://deps.dev/maven/com.microsoft.azure%3Aapplicationinsights-runtime-attach

### `io.github.resilience4j:resilience4j-spring-boot3`

- Location: `eol-checker/samples/build.gradle:77`
- `deps.dev` / Low: io.github.resilience4j:resilience4j-spring-boot3 is behind latest 2.4.0 - https://deps.dev/maven/io.github.resilience4j%3Aresilience4j-spring-boot3

### `io.opentelemetry:opentelemetry-bom`

- Location: `eol-checker/samples/build.gradle:80`
- `deps.dev` / Low: io.opentelemetry:opentelemetry-bom is behind latest 1.63.0 - https://deps.dev/maven/io.opentelemetry%3Aopentelemetry-bom

### `io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom`

- Location: `eol-checker/samples/build.gradle:81`
- `deps.dev` / Low: io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom is behind latest 2.28.1 - https://deps.dev/maven/io.opentelemetry.instrumentation%3Aopentelemetry-instrumentation-bom

### `io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter`

- Location: `eol-checker/samples/build.gradle:85`
- `deps.dev` / Low: io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter is behind latest 2.28.1 - https://deps.dev/maven/io.opentelemetry.instrumentation%3Aopentelemetry-spring-boot-starter

### `org.testcontainers:testcontainers-bom`

- Location: `eol-checker/samples/build.gradle:96`
- `deps.dev` / Low: org.testcontainers:testcontainers-bom is behind latest 2.0.5 - https://deps.dev/maven/org.testcontainers%3Atestcontainers-bom

### `net.datafaker:datafaker`

- Location: `eol-checker/samples/build.gradle:99`
- `deps.dev` / Low: net.datafaker:datafaker is behind latest 2.6.0 - https://deps.dev/maven/net.datafaker%3Adatafaker

### `com.tngtech.archunit:archunit-junit5`

- Location: `eol-checker/samples/build.gradle:100`
- `deps.dev` / Low: com.tngtech.archunit:archunit-junit5 is behind latest 1.4.2 - https://deps.dev/maven/com.tngtech.archunit%3Aarchunit-junit5

### `com.configcat:configcat-java-client`

- Location: `eol-checker/samples/build.gradle:73`
- `deps.dev` / Unknown: com.configcat:configcat-java-client is behind latest 10.0.1 - https://deps.dev/maven/com.configcat%3Aconfigcat-java-client

### `org.springframework.boot:spring-boot-starter-aop`

- Location: `eol-checker/samples/build.gradle:76`
- `deps.dev` / Unknown: org.springframework.boot:spring-boot-starter-aop is behind latest 4.0.0-M2 - https://deps.dev/maven/org.springframework.boot%3Aspring-boot-starter-aop


