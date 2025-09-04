# Composer module for Uniguru-LM
# Handles template-based text composition with n-gram smoothing and GRU fallback

from .compose import compose
from .templates import TemplateEngine
from .ngram_scorer import NGramScorer
from .gru import GRUStub
from .grounding import GroundingVerifier

__all__ = ['compose', 'TemplateEngine', 'NGramScorer', 'GRUStub', 'GroundingVerifier']