# 开发工作流程说明

## Lint Test 详解

### Lint Test 包含的内容：

1. **Flake8** - Python 代码风格检查
   - 检查代码是否符合 PEP 8 规范
   - 检测语法错误和潜在问题
   - 检查代码复杂度

2. **Black** - Python 代码格式化检查
   - 确保代码格式一致性
   - 检查代码是否符合统一的格式标准

3. **Pytest** - 单元测试
   - 运行项目中的测试用例
   - 检查代码功能是否按预期工作
   - 生成代码覆盖率报告

### 是否默认就有？

Lint test 不是默认就有的，你需要：

1. **创建测试文件**：在 `tests/` 目录下编写测试用例
2. **安装测试依赖**：确保 `pyproject.toml` 中包含测试所需的依赖
3. **编写测试代码**：为你的功能编写单元测试

示例测试文件结构：
```
tests/
├── __init__.py
├── test_ingestion.py
├── test_processing.py
└── test_dashboard.py
```

## CI/CD 流程说明

### CI/CD 并不会自动运行应用

CI/CD 流程（lint test → build docker image）完成后：

1. **CI 阶段**：只进行代码检查和测试，不会运行应用
2. **CD 阶段**：构建 Docker 镜像并推送到仓库，但不会自动运行
3. **部署阶段**：只有在特定条件下才会部署到目标环境

### 本地开发 vs CI/CD

| 环境 | 目的 | 如何运行 |
|------|------|----------|
| 本地开发 | 日常开发和调试 | `docker-compose up` |
| CI/CD | 自动化测试和部署 | GitHub Actions 自动运行 |

## 本地开发流程

### 本地运行应用

即使有了 CI/CD，你仍然需要在本地运行 Docker 来开发和测试：

```bash
# 启动整个应用栈（包括 Airflow、Dashboard 等）
docker-compose up

# 或者只启动特定服务
docker-compose up airflow-webserver airflow-scheduler
```

### 本地访问服务

启动后，你可以通过以下地址访问服务：

- **Airflow UI**: http://localhost:8080
- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## CI/CD 与本地开发的关系

### CI/CD 不替代本地开发

CI/CD 是**自动化质量保证和部署流程**，不是**本地开发环境**：

1. **本地开发**：你在本地编写代码、测试、调试
2. **提交代码**：当你提交代码到 GitHub 时，CI/CD 自动运行
3. **质量检查**：CI/CD 检查代码质量和运行测试
4. **构建部署**：如果通过检查，则构建镜像并部署

### 本地开发仍需 Docker Compose

是的，你仍然需要运行 `docker-compose up` 来：

1. **实时开发**：在本地测试你的更改
2. **调试问题**：快速验证功能是否正常工作
3. **查看效果**：在浏览器中查看 Airflow、Dashboard 等界面

## 推荐的开发工作流程

### 日常开发流程

1. **启动本地环境**
   ```bash
   docker-compose up
   ```

2. **在浏览器中查看服务**
   - Airflow: http://localhost:8080
   - Dashboard: http://localhost:8501

3. **编写代码和测试**
   - 在 IDE 中编辑代码
   - 在浏览器中测试功能

4. **提交代码**
   ```bash
   git add .
   git commit -m "描述你的更改"
   git push origin feature/your-feature
   ```

5. **CI/CD 自动运行**
   - 提交后，GitHub Actions 会自动运行测试
   - 如果通过，则构建 Docker 镜像

### 注意事项

- CI/CD 是**质量门禁**，确保代码质量
- 本地开发环境是**功能开发**的主要场所
- 两者相辅相成，不能互相替代
- 本地开发时仍需使用 `docker-compose up` 来运行服务