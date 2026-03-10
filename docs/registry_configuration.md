# Registry 配置指南

## 使用 GitHub Container Registry (GHCR)

由于 Docker Hub 访问问题，我们已将 CI/CD 配置更新为使用 GitHub Container Registry (GHCR)。

### 优势

1. **无缝集成**：与 GitHub 深度集成
2. **无需额外配置**：使用内置的 `GITHUB_TOKEN` 即可
3. **访问控制**：通过 GitHub 仓库权限管理访问
4. **免费配额**：提供充足的免费存储和带宽
5. **性能**：在 GitHub 生态系统内访问速度更快

### 配置详情

当前的 CI/CD 配置使用以下设置：

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

这将使构建的镜像推送到类似以下的地址：
- `ghcr.io/username/repository-name:tag`

### 访问权限

- **读取权限**：公共仓库的镜像是公开可读的
- **写入权限**：需要适当的 GitHub 令牌（已在 CI/CD 中配置）
- **私有仓库**：仅仓库协作者可访问

### 如何启用 Docker Hub 支持（未来）

如果您解决了 Docker Hub 访问问题，可以通过取消注释以下部分来重新启用 Docker Hub 支持：

```yaml
# build-and-push-dockerhub:
#   runs-on: ubuntu-latest
#   needs: lint-test
#   if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/')
#   # This job pushes to Docker Hub, requires secrets.DOCKER_USERNAME and secrets.DOCKER_PASSWORD
#   steps:
#   ...
```

然后在 GitHub 仓库设置中添加以下 Secrets：
- `DOCKER_USERNAME`: Docker Hub 用户名
- `DOCKER_PASSWORD`: Docker Hub 访问令牌

## 关于单元测试的重要性

单元测试是确保代码质量和系统稳定性的重要环节。以下是为什么需要编写单元测试的原因：

### 1. 早期发现问题
- 在开发阶段就能发现代码缺陷
- 减少后期修复成本

### 2. 重构安全保障
- 确保重构过程中功能保持不变
- 提高代码质量的信心

### 3. 文档作用
- 测试用例展示代码的预期行为
- 帮助新团队成员理解代码功能

### 4. CI/CD 集成
- 作为质量门禁，确保只有通过测试的代码才能合并
- 自动化验证代码变更

### 5. 回归测试
- 确保新功能不会破坏现有功能
- 维护系统的整体稳定性

## 推荐的测试策略

1. **从核心功能开始**：优先为关键业务逻辑编写测试
2. **测试覆盖率目标**：建议达到 80% 以上的覆盖率
3. **持续改进**：随着代码增长不断补充测试
4. **集成到开发流程**：确保每次提交都运行测试