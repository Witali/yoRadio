static int httpd_sock_err(const char *ctx, int sockfd)
{
    int errval;
    ESP_LOGW(TAG, LOG_FMT("error in %s : %d"), ctx, errno);

    switch (errno) {
    case EAGAIN:
    case EINTR:
        errval = HTTPD_SOCK_ERR_TIMEOUT;
        break;
    case EINVAL:
    case EBADF:
    case EFAULT:
    case ENOTSOCK:
        errval = HTTPD_SOCK_ERR_INVALID;
        break;
    default:
        errval = HTTPD_SOCK_ERR_FAIL;
    }
    return errval;
}
int httpd_default_send(httpd_handle_t hd, int sockfd, const char *buf, size_t buf_len, int flags)
{
    (void)hd;
    if (buf == NULL) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    int ret = send(sockfd, buf, buf_len, flags);
    if (ret < 0) {
        return httpd_sock_err("send", sockfd);
    }
    return ret;
}
int httpd_default_recv(httpd_handle_t hd, int sockfd, char *buf, size_t buf_len, int flags)
{
    (void)hd;
    if (buf == NULL) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    int ret = recv(sockfd, buf, buf_len, flags);
    if (ret < 0) {
        return httpd_sock_err("recv", sockfd);
    }
    return ret;
}
