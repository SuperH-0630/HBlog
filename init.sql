DROP DATABASE IF EXISTS HBlog;
CREATE DATABASE HBlog;
USE HBlog;

CREATE TABLE IF NOT EXISTS role -- 角色表
(
    RoleID          INT PRIMARY KEY AUTO_INCREMENT,
    RoleName        char(20) NOT NULL UNIQUE,
    WriteBlog       bit DEFAULT 0, -- 写博客
    WriteComment    bit DEFAULT 1, -- 写评论
    WriteMsg        bit DEFAULT 1, -- 写留言
    CreateUser      bit DEFAULT 0, -- 创建新用户

    ReadBlog        bit DEFAULT 1, -- 读博客
    ReadComment     bit DEFAULT 1, -- 读评论
    ReadMsg         bit DEFAULT 1, -- 读留言
    ReadSecretMsg   bit DEFAULT 0, -- 读私密留言
    ReadUserInfo    bit DEFAULT 0, -- 读取用户信息

    DeleteBlog      bit DEFAULT 0, -- 删除博客
    DeleteComment   bit DEFAULT 0, -- 删除评论
    DeleteMsg       bit DEFAULT 0, -- 删除留言
    DeleteUser      bit DEFAULT 0, -- 删除用户

    ConfigureSystem bit DEFAULT 0, -- 配置系统
    ReadSystem      bit DEFAULT 0  -- 读系统信息
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS user -- 创建用户表
(
    ID         INT PRIMARY KEY AUTO_INCREMENT,
    Email      char(32)  NOT NULL UNIQUE,
    PasswdHash char(128) NOT NULL,
    Role       INT       NOT NULL DEFAULT 3,
    FOREIGN KEY (Role) REFERENCES role (RoleID)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

INSERT INTO role (RoleID,
                  RoleName,
                  WriteBlog,
                  WriteComment,
                  WriteMsg,
                  CreateUser,
                  ReadBlog,
                  ReadComment,
                  ReadMsg,
                  ReadSecretMsg,
                  ReadUserInfo,
                  DeleteBlog,
                  DeleteComment,
                  DeleteMsg,
                  DeleteUser,
                  ConfigureSystem,
                  ReadSystem)
VALUES (1, 'Admin', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), -- 管理员用户
       (2, 'Coordinator', 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1); -- 协管员用户

INSERT INTO role (RoleID, RoleName)
VALUES (3, 'Default'); -- 默认用户

INSERT INTO role (RoleID, RoleName, WriteComment, WriteMsg)
VALUES (4, 'Anonymous', 0, 0); -- 默认用户

CREATE TABLE IF NOT EXISTS blog -- 创建博客表
(
    ID         INT PRIMARY KEY AUTO_INCREMENT,              -- 文章 ID
    Auth       INT      NOT NULL,                           -- 作者
    Title      char(20) NOT NULL,                           -- 标题
    SubTitle   char(20) NOT NULL,                           -- 副标题
    Content    TEXT     NOT NULL,                           -- 内容
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建的时间
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,      -- 创建的时间
    Top        BIT      NOT NULL DEFAULT 0,                 -- 置顶
    FOREIGN KEY (Auth) REFERENCES user (ID)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE VIEW blog_with_top AS
SELECT *
FROM blog
ORDER BY Top DESC, UpdateTime DESC;

CREATE TABLE IF NOT EXISTS archive -- 归档表
(
    ID           INT PRIMARY KEY AUTO_INCREMENT, -- 归档 ID
    Name         CHAR(30)  NOT NULL UNIQUE,      -- 归档名称
    DescribeText char(100) NOT NULL              -- 描述
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS blog_archive -- 归档表
(
    BlogID INT, -- 文章ID
    ArchiveID INT, -- 归档ID
    FOREIGN KEY (BlogID) REFERENCES blog (ID),
    FOREIGN KEY (ArchiveID) REFERENCES archive (ID)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE VIEW archive_with_count AS
SELECT ID, Name, DescribeText, (SELECT Count(ArchiveID) FROM blog_archive WHERE blog_archive.ArchiveID = archive.ID) AS Count
FROM archive;

CREATE VIEW blog_archive_with_name AS
SELECT BlogID, ArchiveID, archive.Name As ArchiveName, archive.DescribeText AS DescribeText
FROM blog_archive
LEFT JOIN archive on blog_archive.ArchiveID = archive.ID;

CREATE VIEW blog_with_archive AS
SELECT blog.ID          AS BlogID,
       blog_archive.ArchiveID AS ArchiveID,
       Auth,
       Title,
       SubTitle,
       Content,
       CreateTime,
       UpdateTime,
       Top
FROM blog
         RIGHT JOIN blog_archive ON blog.ID = blog_archive.BlogID;

CREATE TABLE IF NOT EXISTS comment -- 评论表
(
    ID         INT PRIMARY KEY AUTO_INCREMENT,              -- 评论 ID
    BlogID     INT      NOT NULL,                           -- 博客 ID
    Auth       INT      NOT NULL,                           -- 作者
    Content    TEXT     NOT NULL,                           -- 内容
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建的时间
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,      -- 创建的时间
    FOREIGN KEY (BlogID) REFERENCES blog (ID),
    FOREIGN KEY (Auth) REFERENCES user (ID)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE VIEW comment_user AS
SELECT comment.ID as CommentID, BlogID, Auth, user.Email as Email, Content, CreateTime, UpdateTime
FROM comment
         LEFT JOIN user on user.ID = comment.Auth
ORDER BY UpdateTime DESC;

CREATE TABLE IF NOT EXISTS message -- 留言表
(
    ID         INT PRIMARY KEY AUTO_INCREMENT,              -- 留言 ID
    Auth       INT      NOT NULL,                           -- 作者
    Content    TEXT     NOT NULL,                           -- 内容
    Secret     BIT      NOT NULL DEFAULT 0,                 -- 私密内容
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建的时间
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,      -- 创建的时间
    FOREIGN KEY (Auth) REFERENCES user (ID)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;


CREATE VIEW message_user AS
SELECT message.ID as MsgID, Auth, user.Email as Email, Content, CreateTime, UpdateTime, Secret
FROM message
         LEFT JOIN user on user.ID = message.Auth
ORDER BY UpdateTime DESC;
