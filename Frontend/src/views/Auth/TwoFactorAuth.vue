<template>
  <div class="twofa-container">
    <div class="twofa-icon">
      <i class="ti ti-shield-check"></i>
    </div>
    <h2 class="twofa-title">Vérification en deux étapes</h2>
    <p class="twofa-subtitle">Code envoyé à {{ maskedEmail }}</p>
    
    <div class="twofa-code">
      <input
        v-for="(digit, index) in 6"
        :key="index"
        ref="codeInputs"
        type="text"
        maxlength="1"
        class="twofa-digit"
        v-model="code[index]"
        @input="handleInput(index, $event)"
        @keydown="handleKeydown(index, $event)"
        @paste="handlePaste"
        :autofocus="index === 0"
      />
    </div>

    <div class="twofa-actions">
      <button 
        class="btn btn-primary auth-submit" 
        @click="verifyCode"
        :disabled="!isCodeComplete || isLoading"
      >
        <span v-if="!isLoading">Valider et accéder</span>
        <span v-else>Vérification...</span>
      </button>
      
      <div class="twofa-resend" @click="resendCode">
        <i class="ti ti-refresh" :class="{ spinning: isResending }"></i>
        Renvoyer le code
        <span v-if="resendTimer > 0" class="resend-timer">({{ resendTimer }}s)</span>
      </div>
    </div>

    <div class="twofa-note">
      <i class="ti ti-info-circle" style="margin-right:6px"></i>
      Cette étape renforce la sécurité de votre compte. Ne partagez jamais ce code.
    </div>

    <div v-if="error" class="twofa-error">
      <i class="ti ti-alert-circle"></i>
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'TwoFactorAuth',
  
  props: {
    email: {
      type: String,
      required: true
    },
    onVerify: {
      type: Function,
      required: true
    }
  },

  data() {
    return {
      code: ['', '', '', '', '', ''],
      isLoading: false,
      isResending: false,
      resendTimer: 0,
      error: null,
      timerInterval: null
    }
  },

  computed: {
    maskedEmail() {
      if (!this.email) return 'votre email';
      const parts = this.email.split('@');
      if (parts[0].length <= 3) return this.email;
      const masked = parts[0].slice(0, 2) + '***' + parts[0].slice(-1);
      return masked + '@' + parts[1];
    },

    isCodeComplete() {
      return this.code.every(digit => digit !== '');
    }
  },

  mounted() {
    this.$nextTick(() => {
      this.$refs.codeInputs[0]?.focus();
    });
  },

  beforeUnmount() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  },

  methods: {
    handleInput(index, event) {
      const value = event.target.value;
      
      // Ne garder que les chiffres
      if (value && !/^\d$/.test(value)) {
        this.code[index] = '';
        return;
      }

      // Si la valeur est vide, revenir en arrière
      if (!value && index > 0) {
        this.$refs.codeInputs[index - 1].focus();
        return;
      }

      // Passer au champ suivant si une valeur est saisie
      if (value && index < 5) {
        this.$refs.codeInputs[index + 1].focus();
      }

      // Vérifier automatiquement si le code est complet
      if (this.isCodeComplete) {
        this.verifyCode();
      }
    },

    handleKeydown(index, event) {
      // Gérer la touche Backspace
      if (event.key === 'Backspace' && !this.code[index] && index > 0) {
        this.$refs.codeInputs[index - 1].focus();
        this.$refs.codeInputs[index - 1].value = '';
        this.code[index - 1] = '';
      }
    },

    handlePaste(event) {
      event.preventDefault();
      const pastedData = event.clipboardData.getData('text');
      const digits = pastedData.replace(/\D/g, '').slice(0, 6);
      
      if (digits.length > 0) {
        const codeArray = digits.split('');
        this.code = [...codeArray, ...Array(6 - codeArray.length).fill('')];
        
        // Focus sur le dernier champ rempli
        const lastFilledIndex = Math.min(codeArray.length - 1, 5);
        this.$refs.codeInputs[lastFilledIndex].focus();
        
        // Vérifier automatiquement si le code est complet
        if (this.isCodeComplete) {
          this.verifyCode();
        }
      }
    },

    async verifyCode() {
      if (!this.isCodeComplete || this.isLoading) return;
      
      this.isLoading = true;
      this.error = null;

      try {
        const verificationCode = this.code.join('');
        const isValid = await this.onVerify(verificationCode);
        
        if (!isValid) {
          this.error = 'Code invalide. Veuillez réessayer.';
          this.clearCode();
        }
      } catch (err) {
        this.error = 'Une erreur est survenue. Veuillez réessayer.';
        console.error('Erreur de vérification 2FA:', err);
      } finally {
        this.isLoading = false;
      }
    },

    clearCode() {
      this.code = ['', '', '', '', '', ''];
      this.$refs.codeInputs[0]?.focus();
    },

    async resendCode() {
      if (this.isResending || this.resendTimer > 0) return;
      
      this.isResending = true;
      this.error = null;
      
      try {
        // Simuler l'envoi du code
        await new Promise(resolve => setTimeout(resolve, 1500));
        this.startResendTimer();
        this.$emit('resend');
        // Afficher un message de succès
        this.$emit('success', 'Un nouveau code a été envoyé à votre adresse email.');
      } catch (err) {
        this.error = 'Erreur lors de l\'envoi du code. Veuillez réessayer.';
      } finally {
        this.isResending = false;
      }
    },

    startResendTimer() {
      this.resendTimer = 60;
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
      }
      
      this.timerInterval = setInterval(() => {
        this.resendTimer--;
        if (this.resendTimer <= 0) {
          clearInterval(this.timerInterval);
          this.timerInterval = null;
        }
      }, 1000);
    }
  }
}
</script>

<style scoped>
.twofa-container {
  padding: 20px 0;
}

.twofa-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.twofa-icon i {
  font-size: 48px;
  color: var(--primary);
}

.twofa-title {
  text-align: center;
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

.twofa-subtitle {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.twofa-code {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.twofa-digit {
  width: 48px;
  height: 56px;
  text-align: center;
  font-size: 24px;
  font-weight: 500;
  border: 0.5px solid #333333;
  border-radius: 8px;
  background: #121212;
  color: #FFFFFF;
  font-family: 'Inter', sans-serif;
  transition: all 0.2s;
}

.twofa-digit:focus {
  outline: none;
  border: 1.5px solid #F4B400;
  box-shadow: none;
}

.twofa-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.twofa-resend {
  text-align: center;
  font-size: 14px;
  color: #F4B400;
  cursor: pointer;
  transition: opacity 0.2s;
  user-select: none;
}

.twofa-resend:hover {
  opacity: 0.8;
}

.twofa-resend .spinning {
  animation: spin 1s linear infinite;
}

.resend-timer {
  color: var(--text-secondary);
  font-size: 13px;
}

.twofa-note {
  display: flex;
  align-items: center;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  border: 1px solid var(--border-color);
}

.twofa-error {
  margin-top: 16px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: var(--danger);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 480px) {
  .twofa-code {
    gap: 8px;
  }
  
  .twofa-digit {
    width: 40px;
    height: 48px;
    font-size: 20px;
  }
}
</style>
