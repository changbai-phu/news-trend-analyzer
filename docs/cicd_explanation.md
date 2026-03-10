# CI/CD 解释文档

## 什么是CI/CD？

CI/CD代表：
- **CI**: Continuous Integration (持续集成)
- **CD**: Continuous Delivery/Deployment (持续交付/部署)

## CI (持续集成) - Continuous Integration

持续集成是指开发人员频繁地将代码更改合并到中央代码库中的实践。每次合并都会触发自动化流程，包括：

1. **代码拉取**: 从版本控制系统获取最新代码
2. **依赖安装**: 安装项目所需的依赖包
3. **代码检查**: 运行静态代码分析、格式检查等
4. **单元测试**: 运行自动化测试套件
5. **构建**: 将代码编译或打包成可部署的格式

在我们的项目中，`lint-test`作业就是CI的一部分，它负责代码检查和测试。

## CD (持续交付/部署) - Continuous Delivery/Deployment

持续交付/部署是在CI之后的步骤，包括：

- **持续交付**: 代码通过所有测试后，准备好部署到生产环境，但需要手动触发部署
- **持续部署**: 代码通过所有测试后，自动部署到生产环境

在我们的项目中，`build-and-push-image`、`build-and-push-dockerhub`和`deploy-*`作业属于CD部分。

## 两个Docker镜像推送作业的区别

### 1. `build-and-push-image` (推送到GitHub Container Registry)

```yaml
build-and-push-image:
  # 推送镜像到 GitHub Container Registry (GHCR)
  # 优势：
  # - 与GitHub深度集成
  # - 更好的权限控制
  # - 免费配额充足
  # - 访问速度快（特别是GitHub生态内）
```

### 2. `build-and-push-dockerhub` (推送到Docker Hub)

```yaml
build-and-push-dockerhub:
  # 推送镜像到 Docker Hub
  # 优势：
  # - Docker官方仓库，知名度高
  # - 社区广泛使用
  # - 与其他工具集成度高
```

## 为什么要推送到两个地方？

1. **冗余备份**: 避免单点故障，如果一个仓库不可用，可以从另一个获取镜像
2. **访问速度**: 不同地区或网络环境下，访问不同仓库的速度可能不同
3. **团队习惯**: 团队成员可能更熟悉某个特定的镜像仓库
4. **合规要求**: 某些组织可能有特定的镜像仓库要求

## 完整的CI/CD流程

```
代码提交 → CI (代码检查、测试) → CD (构建、推送、部署)
    ↓
代码审查/合并
    ↓
CI: 代码检查和测试
    ↓
CD: 构建Docker镜像
    ↓
CD: 推送到多个镜像仓库
    ↓
CD: 部署到不同环境 (staging/production)
```

## 环境配置

- **开发环境**: feature分支的代码
- **预发布环境**: develop分支的代码
- **生产环境**: release/*分支的代码

每个环境都有自己的配置和密钥，确保安全性。