# Generated by Django 4.2.3 on 2025-02-06 00:18

import app_core.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ACCOUNT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('status', models.CharField(help_text='계정 상태(active, pending, deleted, blocked, banned)', max_length=100)),
                ('note', models.TextField(blank=True, help_text='관리자 메모')),
                ('mileage', models.IntegerField(default=0, help_text='쿠폰 마일리지')),
                ('exp', models.IntegerField(default=0, help_text='레벨업 경험치')),
                ('tel', models.CharField(blank=True, help_text='연락처', max_length=20)),
                ('subsupervisor_permissions', models.CharField(blank=True, help_text='관리자 권한(account, post, coupon, message, banner, setting)', max_length=200)),
                ('recent_ip', models.CharField(blank=True, help_text='최근 접속 IP', max_length=20)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BANNER',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(help_text='위치(top, side)', max_length=20)),
                ('image', models.FileField(help_text='이미지', upload_to=app_core.models.upload_to)),
                ('link', models.CharField(help_text='링크', max_length=300)),
                ('display_weight', models.IntegerField(default=0, help_text='표시 순서')),
            ],
        ),
        migrations.CreateModel(
            name='BLOCKED_IP',
            fields=[
                ('ip', models.CharField(help_text='차단 IP', max_length=20, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='BOARD',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('level_cut', models.IntegerField(default=0, help_text='레벨 제한')),
                ('name', models.CharField(help_text='게시판 이름', max_length=100)),
                ('board_type', models.CharField(help_text='게시물 타입(tree, travel, event, review, board, attendance, greeting, anonymous, qna, coupon)', max_length=20)),
                ('display_weight', models.IntegerField(default=0, help_text='표시 순서')),
                ('comment_groups', models.ManyToManyField(help_text='댓글 그룹', related_name='board_comment_groups', to='auth.group')),
                ('display_groups', models.ManyToManyField(help_text='표시 그룹', related_name='board_display_groups', to='auth.group')),
                ('enter_groups', models.ManyToManyField(help_text='접근 그룹', related_name='board_enter_groups', to='auth.group')),
                ('parent_board', models.ForeignKey(help_text='상위 게시판', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='board_parent_board', to='app_core.board')),
                ('write_groups', models.ManyToManyField(help_text='작성 그룹', related_name='board_write_groups', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='CATEGORY',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='카테고리 이름', max_length=100)),
                ('display_weight', models.IntegerField(default=0, help_text='표시 순서')),
                ('parent_category', models.ForeignKey(help_text='상위 카테고리', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_parent_category', to='app_core.category')),
            ],
        ),
        migrations.CreateModel(
            name='COUPON',
            fields=[
                ('code', models.CharField(help_text='쿠폰 코드', max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='쿠폰 이름', max_length=100)),
                ('image', models.FileField(help_text='이미지', null=True, upload_to=app_core.models.upload_to)),
                ('content', models.TextField(help_text='내용')),
                ('required_mileage', models.IntegerField(default=0, help_text='필요 마일리지')),
                ('expire_at', models.DateTimeField(help_text='만료 일시')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='생성 일시')),
                ('status', models.CharField(default='active', help_text='상태(active, used, expired, deleted)', max_length=20)),
                ('note', models.TextField(help_text='관리자 메모')),
                ('create_account', models.ForeignKey(help_text='생성자', on_delete=django.db.models.deletion.CASCADE, related_name='coupon_create_account', to=settings.AUTH_USER_MODEL)),
                ('own_accounts', models.ManyToManyField(help_text='소유 계정', related_name='coupon_own_accounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LEVEL_RULE',
            fields=[
                ('level', models.IntegerField(primary_key=True, serialize=False)),
                ('image', models.FileField(blank=True, help_text='레벨 이미지', null=True, upload_to=app_core.models.upload_to)),
                ('text', models.CharField(blank=True, help_text='레벨 이름', max_length=20)),
                ('text_color', models.CharField(blank=True, help_text='레벨 텍스트 색상', max_length=20)),
                ('background_color', models.CharField(blank=True, help_text='레벨 배경 색상', max_length=20)),
                ('required_exp', models.IntegerField(help_text='레벨업 필요 경험치')),
            ],
        ),
        migrations.CreateModel(
            name='PLACE_INFO',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('address', models.CharField(help_text='주소', max_length=200)),
                ('location_info', models.CharField(help_text='위치 정보', max_length=200)),
                ('open_info', models.CharField(help_text='영업 정보', max_length=200)),
                ('ad_start_at', models.DateTimeField(auto_now_add=True, help_text='광고 시작 일시')),
                ('ad_end_at', models.DateTimeField(auto_now_add=True, help_text='광고 종료 일시')),
                ('status', models.CharField(default='normal', help_text='상태(writing, normal, pending, ad, blocked)', max_length=20)),
                ('note', models.TextField(help_text='관리자 메모')),
                ('categories', models.ManyToManyField(help_text='카테고리', related_name='place_categories', to='app_core.category')),
            ],
        ),
        migrations.CreateModel(
            name='SERVER_LOG',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(help_text='내용')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='생성 일시')),
            ],
        ),
        migrations.CreateModel(
            name='SERVER_SETTING',
            fields=[
                ('name', models.CharField(help_text='설정 이름', max_length=100, primary_key=True, serialize=False)),
                ('value', models.TextField(help_text='설정 값')),
            ],
        ),
        migrations.CreateModel(
            name='STATISTIC',
            fields=[
                ('name', models.CharField(help_text='통계 이름', max_length=100, primary_key=True, serialize=False)),
                ('value', models.IntegerField(default=0, help_text='통계 값')),
                ('date', models.DateTimeField(auto_now_add=True, help_text='통계 일시')),
            ],
        ),
        migrations.CreateModel(
            name='UPLOAD',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=app_core.models.upload_to)),
            ],
        ),
        migrations.CreateModel(
            name='POST',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='제목', max_length=100)),
                ('image', models.FileField(help_text='대표 이미지', null=True, upload_to=app_core.models.upload_to)),
                ('content', models.TextField(help_text='내용', null=True)),
                ('view_count', models.IntegerField(default=0, help_text='조회수')),
                ('like_count', models.IntegerField(default=0, help_text='좋아요 수')),
                ('search_weight', models.IntegerField(default=0, help_text='검색 가중치')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='작성 일시')),
                ('author', models.ForeignKey(help_text='작성자', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_author', to=settings.AUTH_USER_MODEL)),
                ('boards', models.ManyToManyField(help_text='게시판', related_name='post_boards', to='app_core.board')),
                ('place_info', models.ForeignKey(help_text='여행지 정보', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_place_info', to='app_core.place_info')),
                ('review_post', models.ForeignKey(help_text='리뷰 게시글', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_review_post', to='app_core.post')),
            ],
        ),
        migrations.AddField(
            model_name='place_info',
            name='post',
            field=models.ForeignKey(help_text='게시글', on_delete=django.db.models.deletion.CASCADE, related_name='place_post', to='app_core.post'),
        ),
        migrations.CreateModel(
            name='MESSAGE',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('to_account', models.CharField(help_text='받는 사람', max_length=60)),
                ('sender_account', models.CharField(help_text='보낸 사람', max_length=60)),
                ('title', models.CharField(help_text='제목', max_length=100)),
                ('image', models.FileField(help_text='이미지', null=True, upload_to=app_core.models.upload_to)),
                ('content', models.TextField(help_text='내용')),
                ('is_read', models.BooleanField(default=False, help_text='읽음 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='생성 일시')),
                ('include_coupon', models.ForeignKey(help_text='포함된 쿠폰', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_include_coupon', to='app_core.coupon')),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='post',
            field=models.ForeignKey(help_text='게시글', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_post', to='app_core.post'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='used_account',
            field=models.ManyToManyField(help_text='사용 계정', related_name='coupon_used_account', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='COMMENT',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(help_text='내용')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='작성 일시')),
                ('author', models.ForeignKey(help_text='작성자', on_delete=django.db.models.deletion.CASCADE, related_name='comment_author', to=settings.AUTH_USER_MODEL)),
                ('parent_comment', models.ForeignKey(help_text='상위 댓글', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_parent_comment', to='app_core.comment')),
                ('post', models.ForeignKey(help_text='게시글', on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='app_core.post')),
            ],
        ),
        migrations.CreateModel(
            name='ACTIVITY',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField(help_text='활동 내용')),
                ('exp_change', models.IntegerField(default=0, help_text='경험치 변화')),
                ('mileage_change', models.IntegerField(default=0, help_text='마일리지 변화')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='활동 일시')),
                ('account', models.ForeignKey(help_text='계정', on_delete=django.db.models.deletion.CASCADE, related_name='activity_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='bookmarked_places',
            field=models.ManyToManyField(help_text='즐겨찾기 여행지', related_name='account_bookmarked_places', to='app_core.post'),
        ),
        migrations.AddField(
            model_name='account',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='account',
            name='level',
            field=models.ForeignKey(help_text='사용자 레벨', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_level', to='app_core.level_rule'),
        ),
        migrations.AddField(
            model_name='account',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
