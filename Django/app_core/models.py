from django.db import models
import os
from datetime import datetime
import random
import string
from django.contrib.auth.models import AbstractUser, Group

# ACCOUNT: 계정 테이블
# GROUP: 그룹 테이블
# ACTIVITY: 활동 테이블
# LEVEL_RULE: 레벨 규칙 테이블
# CATEGORY: 카테고리 테이블
# BOARD: 게시판 테이블
# POST: 게시물 테이블
# PLACE_INFO: 여행지 정보 테이블
# COMMENT: 댓글 테이블
# COUPON: 쿠폰 테이블
# MESSAGE: 메시지 테이블
# UPLOAD: 파일 업로드 테이블
# SERVER_SETTING: 서버 설정 테이블
# SERVER_LOG: 서버 로그 테이블
# BANNER: 배너 테이블
# STATISTIC: 통계 테이블
# BLOCKED_IP: 차단 IP 테이블

def upload_to(instance, filename): # 파일 업로드 경로
  _, ext = os.path.splitext(filename)
  new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
  return os.path.join(new_filename)

# ACCOUNT: 계정 테이블
class ACCOUNT(AbstractUser):
  # id = models.AutoField(primary_key=True)
  # username = models.CharField(max_length=150, unique=True) 아이디
  # password = models.CharField(max_length=128)
  # first_name = models.CharField(max_length=30) # 닉네임
  # last_name = models.CharField(max_length=150) # 파트너 업체명
  # email = models.EmailField(max_length=254) # 파트너 이메일
  # is_active = models.BooleanField(default=True)
  # is_staff = models.BooleanField(default=False)
  # is_superuser = models.BooleanField(default=False)
  # date_joined = models.DateTimeField(auto_now_add=True)
  # last_login = models.DateTimeField(auto_now=True)
  # groups = models.ManyToManyField(Group)
  status = models.CharField(max_length=100, help_text='계정 상태(active, pending, deleted, blocked, banned)')
  note = models.TextField(blank=True, help_text='관리자 메모')
  mileage = models.IntegerField(help_text='쿠폰 마일리지', default=0)
  exp = models.IntegerField(help_text='레벨업 경험치', default=0)
  tel = models.CharField(blank=True, max_length=20, help_text='연락처')
  subsupervisor_permissions = models.CharField(blank=True, max_length=200, help_text='관리자 권한(account, post, coupon, message, banner, setting)')
  bookmarked_places = models.ManyToManyField('POST', help_text='즐겨찾기 여행지', related_name='account_bookmarked_places')
  level = models.ForeignKey('LEVEL_RULE', on_delete=models.CASCADE, null=True, help_text='사용자 레벨', related_name='account_level')
  recent_ip = models.CharField(max_length=20, blank=True, help_text='최근 접속 IP')

# GROUP: 그룹 테이블
# class GROUP(models.Model):
# name = models.CharField(primary_key=True)
# permissions = models.ManyToManyField(Permission)

# ACTIVITY: 활동 테이블
class ACTIVITY(models.Model):
  id = models.AutoField(primary_key=True)
  account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='계정', related_name='activity_account')
  message = models.TextField(help_text='활동 내용')
  exp_change = models.IntegerField(help_text='경험치 변화', default=0)
  mileage_change = models.IntegerField(help_text='마일리지 변화', default=0)
  created_at = models.DateTimeField(auto_now_add=True, help_text='활동 일시')

# LEVEL_RULE: 레벨 규칙 테이블
class LEVEL_RULE(models.Model):
  level = models.IntegerField(primary_key=True)
  image = models.FileField(upload_to=upload_to, blank=True, null=True, help_text='레벨 이미지')
  text = models.CharField(max_length=20, blank=True, help_text='레벨 이름')
  text_color = models.CharField(max_length=20, blank=True, help_text='레벨 텍스트 색상')
  background_color = models.CharField(max_length=20, blank=True, help_text='레벨 배경 색상')
  required_exp = models.IntegerField(help_text='레벨업 필요 경험치')

# CATEGORY: 카테고리 테이블
class CATEGORY(models.Model):
  id = models.AutoField(primary_key=True)
  parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 카테고리', related_name='category_parent_category')
  name = models.CharField(max_length=100, help_text='카테고리 이름')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# BOARD: 게시판 테이블
class BOARD(models.Model):
  id = models.AutoField(primary_key=True)
  parent_board = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 게시판', related_name='board_parent_board')
  display_groups = models.ManyToManyField(Group, help_text='표시 그룹', related_name='board_display_groups')
  enter_groups = models.ManyToManyField(Group, help_text='접근 그룹', related_name='board_enter_groups')
  write_groups = models.ManyToManyField(Group, help_text='작성 그룹', related_name='board_write_groups')
  comment_groups = models.ManyToManyField(Group, help_text='댓글 그룹', related_name='board_comment_groups')
  level_cut = models.IntegerField(help_text='레벨 제한', default=0)
  name = models.CharField(max_length=100, help_text='게시판 이름')
  # attendance: 출석 게시판. *특수 게시판
  # greeting: 인사 게시판. *특수 게시판
  # anonymous: 익명 게시판. 모두 글 작성 가능.*특수 게시판
  # qna: 질문 게시판. 모두 글 작성 가능. 댓글은 관리자만 작성 가능.*특수 게시판
  # travel: 여행지 정보 게시판. 파트너만 글 작성 가능.*특수 게시판
  # coupon: 쿠폰 게시판. 파트너와 관리자만 글 작성 가능.*특수 게시판
  # review: 리뷰 게시판. 사용자만 글 작성 가능.*특수 게시판
  # tree: 다른 게시판을 포함하는 게시판. 글 작성 불가.
  # board: 일반 게시판. 모두 글 작성 가능.
  board_type = models.CharField(max_length=20, help_text='게시물 타입(tree, travel, event, review, board, attendance, greeting, anonymous, qna, coupon)')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# POST: 게시물 테이블
class POST(models.Model):
  id = models.AutoField(primary_key=True)
  author = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, null=True, help_text='작성자', related_name='post_author')
  boards = models.ManyToManyField('BOARD', help_text='게시판', related_name='post_boards')
  review_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='리뷰 게시글', related_name='post_review_post')
  place_info = models.ForeignKey('PLACE_INFO', on_delete=models.CASCADE, null=True, help_text='여행지 정보', related_name='post_place_info')
  title = models.CharField(max_length=100, help_text='제목')
  image = models.FileField(upload_to=upload_to, null=True, help_text='대표 이미지')
  content = models.TextField(help_text='내용', null=True)
  view_count = models.IntegerField(help_text='조회수', default=0)
  like_count = models.IntegerField(help_text='좋아요 수', default=0)
  search_weight = models.IntegerField(help_text='검색 가중치', default=0)
  created_at = models.DateTimeField(auto_now_add=True, help_text='작성 일시')

# PLACE_INFO: 여행지 정보 테이블
class PLACE_INFO(models.Model):
  id = models.AutoField(primary_key=True)
  post = models.ForeignKey('POST', on_delete=models.CASCADE, help_text='게시글', related_name='place_post')
  categories = models.ManyToManyField('CATEGORY', help_text='카테고리', related_name='place_categories')
  address = models.CharField(max_length=200, help_text='주소')
  location_info = models.CharField(max_length=200, help_text='위치 정보')
  open_info = models.CharField(max_length=200, help_text='영업 정보')
  ad_start_at = models.DateTimeField(auto_now_add=True, help_text='광고 시작 일시')
  ad_end_at = models.DateTimeField(auto_now_add=True, help_text='광고 종료 일시')
  status = models.CharField(max_length=20, default='normal', help_text='상태(writing, normal, pending, ad, blocked)')
  note = models.TextField(help_text='관리자 메모')

# COMMENT: 댓글 테이블
class COMMENT(models.Model):
  id = models.AutoField(primary_key=True)
  post = models.ForeignKey('POST', on_delete=models.CASCADE, help_text='게시글', related_name='comment_post')
  author = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='작성자', related_name='comment_author')
  parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, help_text='상위 댓글', related_name='comment_parent_comment')
  content = models.TextField(help_text='내용')
  created_at = models.DateTimeField(auto_now_add=True, help_text='작성 일시')

# COUPON: 쿠폰 테이블
class COUPON(models.Model):
  code = models.CharField(max_length=20, primary_key=True, help_text='쿠폰 코드')
  post = models.ForeignKey('POST', on_delete=models.CASCADE, null=True, help_text='게시글', related_name='coupon_post')
  create_account = models.ForeignKey('ACCOUNT', on_delete=models.CASCADE, help_text='생성자', related_name='coupon_create_account')
  own_accounts = models.ManyToManyField('ACCOUNT', help_text='소유 계정', related_name='coupon_own_accounts')
  used_account = models.ManyToManyField('ACCOUNT', help_text='사용 계정', related_name='coupon_used_account') # accounts에 s(복수형) 이름 잘못 적음. 수정 필요
  name = models.CharField(max_length=100, help_text='쿠폰 이름')
  image = models.FileField(upload_to=upload_to, null=True, help_text='이미지')
  content = models.TextField(help_text='내용')
  required_mileage = models.IntegerField(help_text='필요 마일리지', default=0)
  expire_at = models.DateTimeField(help_text='만료 일시')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')
  status = models.CharField(max_length=20, default='active', help_text='상태(active, expired, deleted)')
  note = models.TextField(help_text='관리자 메모')

# MESSAGE: 메시지 테이블
class MESSAGE(models.Model):
  id = models.AutoField(primary_key=True)
  to_account = models.CharField(max_length=60, help_text='받는 사람')
  sender_account = models.CharField(max_length=60, help_text='보낸 사람')
  include_coupon = models.ForeignKey('COUPON', on_delete=models.CASCADE, null=True, help_text='포함된 쿠폰', related_name='message_include_coupon')
  title = models.CharField(max_length=100, help_text='제목')
  image = models.FileField(upload_to=upload_to, null=True, help_text='이미지')
  content = models.TextField(help_text='내용')
  is_read = models.BooleanField(default=False, help_text='읽음 여부')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')

# UPLOAD: 파일 업로드 테이블
class UPLOAD(models.Model):
  file = models.FileField(upload_to=upload_to)

# SERVER_SETTING: 서버 설정 테이블
class SERVER_SETTING(models.Model):
  name = models.CharField(max_length=100, primary_key=True, help_text='설정 이름')
  value = models.TextField(help_text='설정 값')

# SERVER_LOG: 서버 로그 테이블
class SERVER_LOG(models.Model):
  id = models.AutoField(primary_key=True)
  content = models.TextField(help_text='내용')
  created_at = models.DateTimeField(auto_now_add=True, help_text='생성 일시')

# BANNER: 배너 테이블
class BANNER(models.Model):
  id = models.AutoField(primary_key=True)
  location = models.CharField(max_length=20, help_text='위치(top, side)')
  image = models.FileField(upload_to=upload_to, help_text='이미지')
  link = models.CharField(max_length=300, help_text='링크')
  display_weight = models.IntegerField(help_text='표시 순서', default=0)

# STATISTIC: 통계 테이블
class STATISTIC(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100, help_text='통계 이름')
  value = models.IntegerField(help_text='통계 값', default=0)
  date = models.DateTimeField(auto_now_add=True, help_text='통계 일시')

# BLOCKED_IP: 차단 IP 테이블
class BLOCKED_IP(models.Model):
  id = models.AutoField(primary_key=True)
  ip = models.CharField(max_length=20, help_text='차단 IP')
