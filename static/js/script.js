document.addEventListener('DOMContentLoaded', function () {
    // Function to update status icon and text
    function updateStatus(success, message) {
        const statusIcon = document.getElementById('statusIcon');
        const statusMessage = document.getElementById('statusMessage');
        if (success) {
            statusIcon.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
            statusMessage.textContent = ` ${message}`;
        } else {
            statusIcon.innerHTML = '<i class="bi bi-x-circle-fill text-danger"></i>';
            statusMessage.textContent = ` ${message}`;
        }
    }

    function showToast(message) {
    // Get the toast element and the toast body element
    const toastEl = document.getElementById('emptyToast');
    const toastBodyEl = document.getElementById('toastBody');

    // Set the content of the toast body
    toastBodyEl.innerHTML = message;

    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

    function performAction(action) {
        const inputType = document.querySelector('input[name="inputType"]:checked').value;
        const route = inputType === 'bit' ? `/${action}` : `/${action}_ascii`;

        const key = document.getElementById('keyInput').value.split('').map(Number);
        const text = document.getElementById('textInput').value;
        const processedText = inputType === 'bit' ? text.split('').map(Number) : text;
        if (key.length === 0) {
            showToast('请输入密钥');
            return;
        }
        if (processedText.length === 0) {
            showToast('请输入明文或密文');
            return;
        }

        fetch(route, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({key, text: processedText})
        }).then(response => response.json()).then(data => {
            document.getElementById('outputText').textContent = inputType === 'bit' ? data.result.join('') : data.result;
            updateStatus(true, `${action.charAt(0).toUpperCase() + action.slice(1)} successful`);
        }).catch(error => {
            updateStatus(false, `${action.charAt(0).toUpperCase() + action.slice(1)} failed`);
        });
    }

    document.getElementById('encryptBtn').addEventListener('click', function () {
        performAction('encrypt');
    });

    document.getElementById('decryptBtn').addEventListener('click', function () {
        performAction('decrypt');
    });

    document.getElementById('addPairBtn').addEventListener('click', function () {
        // 获取用户输入的明文和密文
        const plaintextInput = document.querySelector('.plaintext');
        const ciphertextInput = document.querySelector('.ciphertext');

        // 获取无序列表
        const pairsList = document.getElementById('pairsList');

        // 获取明文和密文输入框的值
        const plaintext = plaintextInput.value.trim();
        const ciphertext = ciphertextInput.value.trim();

        // 只有当明文和密文都不为空时，才添加到无序列表中
        if (plaintext && ciphertext) {
            // 创建一个新的列表项
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.textContent = `明文: ${plaintext}, 密文: ${ciphertext}`;

            // 将新的列表项添加到无序列表中
            pairsList.appendChild(listItem);

            // 清空输入框
            plaintextInput.value = '';
            ciphertextInput.value = '';
        }
    });
    document.querySelector('.forceBtn').addEventListener('click', function () {
        const pairsList = document.getElementById('pairsList');
        const pairs = Array.from(pairsList.children).map(li => {
            const text = li.textContent || li.innerText;
            const [plaintextStr, ciphertextStr] = text.split(',').map(s => s.split(':')[1].trim());
            return {
                plaintext: plaintextStr,
                ciphertext: ciphertextStr
            };
        });
        if (pairs.length === 0) {
            showToast('请添加明文和密文对');
            return;
        }
        // 显示模态框
        const bruteForceModal = new bootstrap.Modal(document.getElementById('bruteForceModal'));
        bruteForceModal.show();
        // 将明文和密文对发送到后端
        fetch('/brute_force', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({pairs})
        }).then(response => response.json()).then(data => {
            // 更新模态框的内容并显示找到的密钥和所花费的时间
            // 隐藏旋转器
            document.getElementById('spinnerContainer').classList.add('d-none');
            // $('spinner').hide();
            document.getElementById('modalText').innerHTML = `密钥已找到: ${data.key.join('')}<br>花费时间: ${data.time_taken} seconds`;
        }).catch(error => {
            // 如果出错，更新模态框的内容并显示错误消息
            // 隐藏旋转器
            document.getElementById('spinnerContainer').classList.add('d-none');
            document.getElementById('modalText').textContent = 'Brute force failed';
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
        function showToast(message) {
    // Get the toast element and the toast body element
    const toastEl = document.getElementById('emptyToast');
    const toastBodyEl = document.getElementById('toastBody');

    // Set the content of the toast body
    toastBodyEl.textContent = message;

    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
    document.querySelector('.forceBtnAll').addEventListener('click', function () {
        const pairsList = document.getElementById('pairsList');
        const pairs = Array.from(pairsList.children).map(li => {
            const text = li.textContent || li.innerText;
            const [plaintextStr, ciphertextStr] = text.split(',').map(s => s.split(':')[1].trim());
            return {
                plaintext: plaintextStr,
                ciphertext: ciphertextStr
            };
        });
        if (pairs.length === 0) {
            showToast('请添加明文和密文对');
            return;
        }
        // 发送暴力破解请求到后端
        fetch('/brute_force_all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({pairs})
        }).then(response => response.json()).then(data => {
            const keysList = document.getElementById('keysList');

            // 清空列表
            keysList.innerHTML = '';

            // 添加所有找到的密钥到列表中
            data.keys.forEach(key => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.textContent = key.join('');
                keysList.appendChild(listItem);
            });
            // 显示总时间
            timeTaken.textContent = `总时间: ${data.time_taken} 秒`;

        }).catch(error => {
            // 如果出错，显示错误消息
            console.error('Error during brute force:', error);
        });
    });
});
