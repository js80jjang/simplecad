@echo off
chcp 65001 >nul
echo ==============================
echo  GitHub 저장소 설정 스크립트
echo ==============================
echo.

cd /d "%~dp0"

:: 기존 .git 폴더가 있으면 삭제
if exist ".git" (
    echo 기존 .git 폴더 삭제 중...
    rmdir /s /q ".git"
)

:: git 초기화
echo git 초기화 중...
git init -b main
git config user.email "js80jjang@gmail.com"
git config user.name "junseob"

:: 원격 저장소 연결
echo 원격 저장소 연결 중...
git remote add origin https://github.com/js80jjang/simplecad.git

:: 파일 추가 및 커밋
echo 파일 추가 중...
git add .
git commit -m "초기 커밋: 세라믹 가공비 계산기"

:: GitHub에 push
echo.
echo GitHub에 push 중... (GitHub 로그인 창이 뜰 수 있습니다)
git push -u origin main

echo.
echo ==============================
echo  완료!
echo  https://github.com/js80jjang/simplecad 에서 확인하세요
echo ==============================
pause
