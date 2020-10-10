# Смартконтракты
На Ethereum

## Ресурсы
[Компилятор](https://remix.ethereum.org/)

Управление кошельками: [chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#](chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#)

[Начисление токенов](https://faucet.ropsten.be/), [Начисление токенов](https://faucet.metamask.io/)

[Проверка кошелька](https://ropsten.etherscan.io/address/0xa561c73b64a43cb3aeb7dfbbfd1d6a4c9fe8ddc5)

[Проверка транзакций](https://ropsten.etherscan.io/tx/0x6f2d71f0cfefada5bafa5d49052b20cfdff13a4fbf917864e5067c79c54bdbc2)

## Написание контракта

## Запуск контракта
1. Настроить MetaMask расширение для Chrome
2. Переключиться на тестовую сеть Ropsten
3. Получить токены из Faucet
4. Открыть https://remix.ethereum.org/
5. Создать файл со своим кодом
6. Активировать расширения "SOLIDITY COMPILER" & "DEPLOY & RUN TRANSACTIONS"
7. Переключиться на вкладку компиляции
8. Нажать "Compile"
9. Переключиться на вкладку развёртки
10. Выбрать "Injected Web3" в "Environment"
11. Указать стартовые параметры контракта и нажать "Deploy"
12. В открывшемся окне MetaMask подтвердить операцию
13. Проверить в MetaMask, что идёт процесс развёртывания контракта
14. Когда развёртка завершится, контракт появится в разделе "Deployed Contracts"
15. Здесь отображаются все функции контракта, можно использовать и тестировать

## Внедрение в JS приложение