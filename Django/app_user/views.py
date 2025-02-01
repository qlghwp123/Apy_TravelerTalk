import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models
from app_core import daos

# 메인 페이지
# 광고 베너, 사용자 활동 요약, 추천 콘텐츠 및 이벤트 정보 표시
# 모든 여행지 게시글을 weight룰 기준으로 정렬하여 보여줌
def index(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 데이터 가져오기
  page = int(request.GET.get('page', '1'))
  search = request.GET.get('search', '')

  # 배너 정보 가져오기
  banners = daos.get_display_banners()

  # 메인 페에지에 표시할 여행지 게시글 가져오기
  posts = []
  ps = models.POST.objects.select_related('author', 'place_info').prefetch_related('place_info__categories').exclude(
    review_post__isnull=True
  ).filter(
    title__contains=search, # 검색어가 제목에 포함된 경우
    place_info__status='ad' # post > place_info > status가 'ad'인 경우
  ).order_by('search_weight')
  last_page = (ps.count() // 20) + 1
  ps = ps[(page - 1) * 20:page * 20] # 각 페이지에 20개씩 표시
  for p in ps:
    posts.append({
      'id': p.id,
      'title': p.title,
      'author': {
        'nickname': p.author.first_name,
      },
      'place_info': {
        'categories': [c.name for c in p.place_info.categories],
        'address': p.place_info.address,
        'location_info': p.place_info.location_info,
        'open_info': p.place_info.open_info,
        'status': 'ad',
      },
      'view_count': p.view_count,
      'like_count': p.like_count,
      'created_at': p.created_at,
    })

  return render(request, 'index.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'banners': banners, # 배너 정보
    'posts': posts, # 여행지 게시글 정보
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 회원가입 페이지
def signup(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 이미 로그인된 경우, 리다이렉트 후 메세지 표시
  if request.user.is_authenticated:
    return redirect('/?redirect_message=already_login')

  # 여행지 게시판 정보
  travel_boards = daos.get_travel_board_tree()

  # 카테고리 정보
  categories = daos.get_category_tree()

  return render(request, 'signup.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'travel_boards': travel_boards, # 여행지 게시판 정보
    'categories': categories, # 카테고리 정보
  })

# 계정 찾기 페이지
# 계정 찾기는 관리자 문의를 통해 가능함
def find_account(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 이미 로그인된 경우, 리다이렉트 후 메세지 표시
  if request.user.is_authenticated:
    return redirect('/?redirect_message=already_login')

  return render(request, 'find_account.html', {
    **contexts,
    'boards': boards, # 게시판 정보
  })

# 프로필 페이지
# 관릐자의 경우, 다른 계정의 프로필 조회 가능.
def profile(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 로그인 되지 않은 경우, 리다이렉트 후 로그인 필요 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=need_login')

  # data
  # 최상위 관리자 또는 사용자 권한이 있는 부관리자 계정일 경우, 다른 사용자의 프로필 페이지 접근 가능
  if account_type == 'supervisor' or account_type == 'subsupervisor':
    profile_id = request.GET.get('profile_id', request.user.username)
  else: # 그 외의 경우, 자신의 프로필 페이지만 접근 가능
    profile_id = request.user.username

  # 프로필 정보 가져오기
  profile = daos.get_user_profile_by_id(profile_id)

  # 레벨 규칙 정보
  # 사용자만 레벨 규칙 정보를 가져옴
  level_rules = daos.get_all_level_rules()

  # 카테고리 정보
  # 파트너만 카테고리 정보를 가져옴
  categories = daos.get_category_tree()

  return render(request, 'profile.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'profile': profile, # 사용자 또는 profile_id에 해당하는 사용자의 프로필 정보
    'level_rules': level_rules, # 사용자의 레벨 규칙 정보
    'categories': categories, # 파트너의 카테고리 정보 수정에 필요.
  })

# 활동 페이지
# 관리자와 파트너는 다른 사용자의 활동 페이지를 조회 가능.
def activity(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 로그인 되지 않은 경우, 리다이렉트 후 로그인 필요 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=need_login')

  # data
  page = int(request.GET.get('page', '1'))

  # 관리자 또는 파트너 확인 가능
  if account_type == 'supervisor' or account_type == 'partner' or account_type == 'subsupervisor':
    profile_id = request.GET.get('profile_id', request.user.username)
  else: # 그 외의 경우, 자신의 활동 페이지만 접근 가능
    profile_id = request.user.username

  # 프로필 정보도 같이 가져옴
  profile = daos.get_user_profile_by_id(profile_id)

  # 프로필의 활동 내역 가져오기
  activities, last_page = daos.get_user_activities(profile_id, page)

  return render(request, 'activity.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'profile': profile, # 사용자 또는 profile_id에 해당하는 사용자의 프로필 정보
    'activities': activities, # 사용자 또는 profile_id에 해당하는 사용자의 활동 내역
    'last_page': last_page, # 페이지 처리를 위해 필요한 정보
  })

# 북마크 페이지
def bookmark(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 로그인 되지 않은 경우, 리다이렉트 후 로그인 필요 메세지 표시
  if not request.user.is_authenticated:
    return redirect('/?redirect_message=need_login')

  bookmarks = daos.get_all_bookmarked_places(request.user.username)

  return render(request, 'bookmark.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'bookmarks': bookmarks,
  })

# 제휴 문의 페이지
def contact(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  return render(request, 'contact.html', {
    **contexts,
    'boards': boards, # 게시판 정보
  })

# 이용약관 페이지
def terms(request):
  contexts = daos.get_default_contexts(request) # 기본 컨텍스트 정보 가져오기
  account_type = 'guest' # 기본값은 guest
  if request.user.is_authenticated:
    account_type = 'user'
    if 'dame' in contexts['account']['groups']:
      account_type = 'dame'
    elif 'partner' in contexts['account']['groups']:
      account_type = 'partner'
    elif 'subsupervisor' in contexts['account']['groups']:
      account_type = 'subsupervisor'
    elif 'supervisor' in contexts['account']['groups']:
      account_type = 'supervisor'
  contexts['account']['account_type'] = account_type
  boards = daos.get_board_tree(account_type) # 게시판 정보

  # 이용약관 본문 가져오기
  terms = models.SERVER_SETTING.objects.get(name='terms').value

  return render(request, 'terms.html', {
    **contexts,
    'boards': boards, # 게시판 정보
    'terms': terms,
  })
