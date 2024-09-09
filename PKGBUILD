# Maintainer: C (Sneg) wblmmn@gmail.com

pkgname=todo-cli
pkgver=0.1.0
pkgrel=1
pkgdesc="A command-line interface tool for managing tasks using the Todo.txt format with extends"
arch=('any')
url="https://github.com/ci-c/todo-cli"
license=('MIT')
depends=('python' 'python-click')
makedepends=('python-setuptools')
source=("$pkgname-$pkgver.tar.gz::https://github.com/ci-c/todo-cli/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$srcdir/$pkgname-$pkgver"
    python setup.py build
}

package() {
    cd "$srcdir/$pkgname-$pkgver"
    python setup.py install --root="$pkgdir" --optimize=1 --skip-build
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
